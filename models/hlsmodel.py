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

class ApController:
    def __init__(self, name: str, control_start_pin: int, state_monitor_pin: int):
        self.name = name
        self.start_o    = GPIO(GPIO.get_gpio_pin(control_start_pin+0x00), 'out')
        self.compl_o    = GPIO(GPIO.get_gpio_pin(control_start_pin+0x01), 'out')
        self.done_i     = GPIO(GPIO.get_gpio_pin(control_start_pin+0x02), 'in')
        self.idle_i     = GPIO(GPIO.get_gpio_pin(control_start_pin+0x03), 'in')
        self.ap_start   = GPIO(GPIO.get_gpio_pin(state_monitor_pin+0x00), 'in')
        self.ap_done    = GPIO(GPIO.get_gpio_pin(state_monitor_pin+0x01), 'in')
        self.ap_ready   = GPIO(GPIO.get_gpio_pin(state_monitor_pin+0x02), 'in')
        self.ap_idle    = GPIO(GPIO.get_gpio_pin(state_monitor_pin+0x03), 'in')
    
    def state_str(self):
        return (f"State:{self.done_i.read()}{self.idle_i.read()}{self.ap_start.read()}"
                f"{self.ap_done.read()}{self.ap_ready.read()}{self.ap_idle.read()}")

    def wait_to_complete(self):
        self.compl_o.write(1)
        cnt=0
        while not self.idle_i.read() or self.done_i.read():
            cnt+=1
            print(f"{cnt}:wait {self.name} to complete({self.state_str()})...",
                  end='\r')
        self.compl_o.write(0)
    
    def start(self):
        self.start_o.write(1)
        cnt = 0
        while self.idle_i.read() and not self.done_i.read():
            cnt += 1
            print(f"{cnt}: wait {self.name} to start({self.state_str})...", end='\r')
        self.start_o.write(0)

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
        # TODO: Option not to reset, use internal cache to speed up loading
        _logger.info("Resetting PL...")
        pynq.PL.reset()
        _logger.info("Loading overlay...")
        self.overlay = pynq.Overlay(bitfile_path)

        _logger.info("Instantiating IP drivers...")
        self.ip_forward = self.overlay.forward
        self.ip_backward = self.overlay.backward
        self.ip_param_loader = self.overlay.param_loader
        self.ip_grad_extractor = self.overlay.grad_extractor

        self.sys_reset_o   = GPIO(GPIO.get_gpio_pin(0x10), 'out')
        self.pa_reset_o    = GPIO(GPIO.get_gpio_pin(0x11), 'out')
        self.gr_reset_o    = GPIO(GPIO.get_gpio_pin(0x12), 'out')

        self.pa_rst_busy_i = GPIO(GPIO.get_gpio_pin(0x14), 'in')
        self.gr_rst_busy_i = GPIO(GPIO.get_gpio_pin(0x15), 'in')

        self.cache_en_o    = GPIO(GPIO.get_gpio_pin(0x18), 'out')

        self.bram_sel_o    = GPIO(GPIO.get_gpio_pin(0x19), 'out')

        self.fw_ap = ApController("fw", 0x00, 0x20)
        self.bw_ap = ApController("bw", 0x04, 0x24)
        self.pa_ap = ApController("pa", 0x08, 0x28)
        self.gr_ap = ApController("gr", 0x0c, 0x2c)
        
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
        self.params = params.detach().requires_grad_(True)

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

        self.pa_ap.wait_to_complete()

        self.ip_param_loader.mmio.write(
            self.ip_param_loader.register_map.in_r.address,
            get_float_pointer(self.params.detach())
        )

        self.pa_ap.start()
        self.pa_ap.wait_to_complete()

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
        self.cache_en_o.write(1 if requires_grad else 0)

        for i, o in enumerate(obs):
            self.fw_ap.wait_to_complete()
            print(f"Forwarding #{i:2d}...", end="\r")
            self.ip_forward.mmio.write(
                self.ip_forward.register_map.maxi_x.address,
                get_float_pointer(o))
            self.ip_forward.mmio.write(
                self.ip_forward.register_map.maxi_y.address,
                get_float_pointer(holder[i]))
            self.fw_ap.start()

        self.fw_ap.wait_to_complete()

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
        self.bram_sel_o.write(1)


        for i, g in enumerate(grads):
            print(f"Backwarding #{i:2d}...", end="\r")
            self.bw_ap.wait_to_complete()
            self.ip_backward.mmio.write(
                self.ip_backward.register_map.maxi_grad_y.address,
                get_float_pointer(g)
            )
            self.bw_ap.start()

        self.bw_ap.wait_to_complete()
        
    def _actual_zero_grad(self):
        self.gr_reset_o.write(1)
        time.sleep(0)
        self.gr_reset_o.write(0)
        while self.gr_rst_busy_i.read():
            time.sleep(0)

    def _extract_grads(self):
        self.bram_sel_o.write(0)

        self.gr_ap.wait_to_complete()
        
        self.ip_grad_extractor.mmio.write(
            self.ip_grad_extractor.register_map.out_r.address,
            get_float_pointer(self.grads)
        )
        self.gr_ap.start()
        self.gr_ap.wait_to_complete()
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
