from itertools import chain
import os
from models.interfaces import AbstractActorCritic
import torch
from typing import Callable, Tuple
import pynq
from pynq import GPIO
import time
import logging
from cm_type import get_float_pointer, torch_cm_float

from models.pymodel import PyModel

_logger = logging.getLogger("HlsActorCritic")

class _FuncFlipFlop:
    def __init__(self, func: Callable[[None], None]) -> None:
        self.func = func
        self.diff = 0
    def flip(self):
        self.diff += 1
        if self.diff == 0:
            self.func()
        assert(self.diff < 2)
    def flop(self):
        self.diff -= 1
        if self.diff == 0:
            self.func()
        assert(self.diff > -2)

class HlsActorCritic(AbstractActorCritic):
    def __init__(self, obs_dim, act_dim, /, lr_actor=0.0001, lr_critic=0.001, hidden_width=64, act_continuous=True, use_orthogonal_init=False) -> None:
        super().__init__(obs_dim, act_dim, lr_actor, lr_critic, hidden_width, act_continuous, use_orthogonal_init)
        _logger.info("Constructing HlsActorCritic...")

        self._init_backend()

        self._init_net_parameters(lr_critic, lr_actor, use_orthogonal_init)

        self._init_holders()

        self.backward_fff = _FuncFlipFlop(self._actual_backward)
        self.step_fff = _FuncFlipFlop(self._actual_step)
        self.zero_grad_fff = _FuncFlipFlop(self._actual_zero_grad)

    def _init_holders(self):
        self.grads = torch.zeros_like(self.params)

    def _init_backend(self):
        bitfile_path = os.path.join(
            os.path.dirname(__file__),
            'hlsmodel_src',
            f'generated.system.{self.obs_dim}.{self.act_dim}.{self.hidden_width}.{1 if self.act_continuous else 0}.bit')
        assert(os.path.exists(bitfile_path))
        # Use internal cache to speed up loading
        # _logger.info("Resetting PL...")
        # pynq.PL.reset()
        _logger.info("Loading overlay...")
        self.overlay = pynq.Overlay(bitfile_path)

        _logger.info("Instantiating IP drivers...")
        self.ip_forward = self.overlay.forward
        self.ip_backward = self.overlay.backward
        self.ip_param_loader = self.overlay.param_loader
        self.ip_grad_extractor = self.overlay.grad_extractor

        self.fw_start_o    = GPIO(GPIO.get_gpio_pin(0x00), 'out')
        self.fw_compl_o    = GPIO(GPIO.get_gpio_pin(0x01), 'out')
        self.fw_done_i     = GPIO(GPIO.get_gpio_pin(0x02), 'in')
        self.fw_idle_i     = GPIO(GPIO.get_gpio_pin(0x03), 'in')

        self.bw_start_o    = GPIO(GPIO.get_gpio_pin(0x04), 'out')
        self.bw_compl_o    = GPIO(GPIO.get_gpio_pin(0x05), 'out')
        self.bw_done_i     = GPIO(GPIO.get_gpio_pin(0x06), 'in')
        self.bw_idle_i     = GPIO(GPIO.get_gpio_pin(0x07), 'in')

        self.pa_start_o    = GPIO(GPIO.get_gpio_pin(0x08), 'out')
        self.pa_compl_o    = GPIO(GPIO.get_gpio_pin(0x09), 'out')
        self.pa_done_i     = GPIO(GPIO.get_gpio_pin(0x0a), 'in')
        self.pa_idle_i     = GPIO(GPIO.get_gpio_pin(0x0b), 'in')

        self.gr_start_o    = GPIO(GPIO.get_gpio_pin(0x0c), 'out')
        self.gr_compl_o    = GPIO(GPIO.get_gpio_pin(0x0d), 'out')
        self.gr_done_i     = GPIO(GPIO.get_gpio_pin(0x0e), 'in')
        self.gr_idle_i     = GPIO(GPIO.get_gpio_pin(0x0f), 'in')

        self.sys_reset_o   = GPIO(GPIO.get_gpio_pin(0x10), 'out')
        self.pa_reset_o    = GPIO(GPIO.get_gpio_pin(0x11), 'out')
        self.gr_reset_o    = GPIO(GPIO.get_gpio_pin(0x12), 'out')

        self.pa_rst_busy_i = GPIO(GPIO.get_gpio_pin(0x14), 'in')
        self.gr_rst_busy_i = GPIO(GPIO.get_gpio_pin(0x15), 'in')

        self.cache_en_o    = GPIO(GPIO.get_gpio_pin(0x18), 'out')

        self.bram_sel_o    = GPIO(GPIO.get_gpio_pin(0x19), 'out')
        
        _logger.info("Resetting PL IPs...")
        self.sys_reset_o.write(1)
        time.sleep(0.001)
        self.sys_reset_o.write(0)
        _logger.info("Done!")

    def _init_net_parameters(self, lr_critic, lr_actor, use_orthogonal_init):
        _logger.info("Generating initial parameters...")
        pymodel = PyModel(
            self.obs_dim,
            self.act_dim,
            self.hidden_width,
            self.act_continuous,
            use_orthogonal_init
        )
        x = list(chain(
            pymodel.critic_net.parameters(),
            pymodel.act_feat_net.parameters(),
            pymodel.mu_net.parameters(),
            pymodel.rho_net.parameters()
        ))
        for i in range(len(x)):
            if len(x[i].shape) > 1:
                x[i] = x[i].flatten()
        params = torch.concat(x)

        del pymodel

        self._set_net_parameters(lr_critic=lr_critic, lr_actor=lr_actor, params=params)

    def _set_net_parameters(self, /, lr_critic: float, lr_actor: float, params: torch.Tensor):
        self.lr_critic_modifier = lr_critic / lr_actor

        if params.dtype != torch_cm_float:
            params = torch.tensor(params, dtype=torch_cm_float)
        self.params = params

        self.params.requires_grad_(True)

        self._apply_params()

        assert(self.act_continuous)
        self.optim = torch.optim.Adam(
            [self.params],
            lr=lr_actor,
            eps=1e-5
        )

    def _apply_params(self):
        _logger.info("Parameters syncing out...")
        self.bram_sel_o.write(0)

        self.pa_compl_o.write(1)
        while not self.pa_idle_i.read() or self.pa_done_i.read():
            print("Wait pa to be idle...")
            time.sleep(0)
        self.pa_compl_o.write(0)

        self.ip_param_loader.mmio.write(
            self.ip_param_loader.register_map.in_r.address,
            get_float_pointer(self.params.detach())
        )

        self.pa_start_o.write(1)
        while not self.pa_done_i.read():
            _logger.info("Still syncing...")
            time.sleep(0)
        self.pa_start_o.write(0)
        self.pa_compl_o.write(1)
        while self.pa_done_i.read():
            time.sleep(0)
        self.pa_compl_o.write(0)


        _logger.info("Parameters syncing finished!")

    @property
    def lr_critic(self):
        return self.lr_actor * self.lr_critic_modifier
    
    @lr_critic.setter
    def lr_critic(self, value):
        self.lr_critic_modifier = value / self.lr_actor

    @property
    def lr_actor(self):
        return self.optim.param_groups[0]['lr']
    
    @lr_actor.setter
    def lr_actor(self, value):
        for p in self.optim.param_groups:
            p['lr'] = value

    def forward(self, obs: torch.Tensor, requires_grad=False) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        holder = torch.zeros((len(obs), self.act_dim * 2 + 1), dtype=torch_cm_float)
        mu = holder[:, 0:self.act_dim]
        sigma = holder[:, self.act_dim:self.act_dim*2]
        value = holder[:, self.act_dim*2:]

        self.bram_sel_o.write(1)
        self.cache_en_o.write(requires_grad)

        self.fw_compl_o.write(1)
        while not self.fw_idle_i.read() or self.fw_done_i.read():
            print("Wait fw to be idle...")
            time.sleep(0)
        self.fw_compl_o.write(0)

        for i, o in enumerate(obs):
            print(f"Forwarding #{i:2d}...", end="\r")
            self.ip_forward.mmio.write(
                self.ip_forward.register_map.maxi_x.address,
                get_float_pointer(o))
            self.ip_forward.mmio.write(
                self.ip_forward.register_map.maxi_y.address,
                get_float_pointer(holder[i]))
        
            self.fw_start_o.write(1)
            cnt = 0
            while not self.fw_done_i.read():
                cnt += 1
                print(f"Waiting {cnt}...", end="\r")
                time.sleep(0)
            self.fw_start_o.write(0)
            self.fw_compl_o.write(1)
            while not self.fw_idle_i.read():
                time.sleep(0)
            self.fw_compl_o.write(0)


        return (value.detach().requires_grad_(requires_grad),
                mu.detach().requires_grad_(requires_grad),
                sigma.detach().requires_grad_(requires_grad))

    def act(self, obs: torch.Tensor, requires_grad=False) -> Tuple[torch.Tensor, torch.Tensor]:
        # To avoid messing up cache
        assert(not requires_grad)
        return self.forward(obs, requires_grad)[1:]

    def critic(self, obs: torch.Tensor, requires_grad=False) -> torch.Tensor:
        # To avoid messing up cache
        assert(not requires_grad)
        return self.forward(obs, requires_grad)[0]

    def _actual_backward(self):
        grads: torch.Tensor = torch.concat(
            (self.mu_grad,
             self.std_grad,
             self.value_grad*self.lr_critic_modifier),
            dim=-1)

        if len(grads.shape) == 1:
            grads = grads.unsqueeze(0)

        assert(len(grads.shape) == 2)

        self.bw_compl_o.write(1)
        while not self.bw_idle_i.read() or self.bw_done_i.read():
            print("Wait bw to be idle...")
            time.sleep(0)
        self.bw_compl_o.write(0)

        i = 0
        for g in grads:
            i += 1
            print(f"Backwarding #{i:2d}...", end="\r")
            self.ip_backward.mmio.write(
                self.ip_backward.register_map.maxi_grad_y.address,
                get_float_pointer(g)
            )
            self.bw_start_o.write(1)
            cnt = 0
            while not self.bw_done_i.read():
                cnt += 1
                print(f"Waiting {cnt}...", end="\r")
                time.sleep(0)
            self.bw_start_o.write(0)
            self.bw_compl_o.write(1)
            while not self.bw_idle_i.read():
                time.sleep(0)
            self.bw_compl_o.write(0)
        
    def _actual_zero_grad(self):
        self.gr_reset_o.write(1)
        self.gr_reset_o.write(0)
        while self.gr_rst_busy_i.read():
            time.sleep(0)

    def _extract_grads(self):
        self.bram_sel_o.write(0)
        self.gr_compl_o.write(1)
        while not self.gr_idle_i.read():
            print("Wait gr to be idle...")
            time.sleep(0)
        self.gr_compl_o.write(0)
        self.ip_grad_extractor.mmio.write(
            self.ip_grad_extractor.register_map.out_r.address,
            get_float_pointer(self.grads)
        )
        self.gr_start_o.write(1)
        cnt = 0
        while self.gr_idle_i.read() or self.gr_done_i.read():
            cnt += 1
            print(f"Waiting {cnt}...", end="\r")
            time.sleep(0)
        self.gr_start_o.write(0)
        self.gr_compl_o.write(1)
        while not self.gr_idle_i.read():
            time.sleep(0)
        self.gr_compl_o.write(0)
        self.params.grad = self.grads

    def _actual_step(self):
        self._extract_grads()
        self.optim.step()
        self._apply_params()

    def actor_backward(self, mu_grad, std_grad):
        self.mu_grad = mu_grad
        self.std_grad = std_grad
        self.backward_fff.flip()

    def critic_backward(self, value_grad):
        self.value_grad = value_grad
        self.backward_fff.flop()

    def actor_zero_grad(self):
        self.zero_grad_fff.flip()

    def critic_zero_grad(self):
        self.zero_grad_fff.flop()

    def actor_step(self):
        self.step_fff.flip()

    def critic_step(self):
        return self.step_fff.flop()

    def save(self, filename):
        sd = {
            'model':self.params,
            'act_continuous':self.act_continuous,
            'optim':self.optim.state_dict()
        }
        torch.save(sd, filename)

    def load(self, filename):
        sd = torch.load(filename)

        params = sd['model']
        self._set_net_parameters(
            lr_critic=self.lr_critic,
            lr_actor=self.lr_actor,
            params=params)
        assert(self.act_continuous == sd['act_continuous'])
        self.optim.load_state_dict(sd['optim'])
