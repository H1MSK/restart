from itertools import chain
import os
from models.interfaces import AbstractActorCritic
from ctypes import c_float, c_bool, POINTER
import torch
from typing import Callable, Tuple
import pynq
from pynq import GPIO
import time
import numpy as np

from models.pymodel import PyModel

cm_float = c_float
torch_cm_float = torch.float32
cm_float_p = POINTER(cm_float)

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

class HlsSimActorCritic(AbstractActorCritic):
    def __init__(self, obs_dim, act_dim, /, lr_actor=0.0001, lr_critic=0.001, hidden_width=64, act_continuous=True, use_orthogonal_init=False) -> None:
        super().__init__(obs_dim, act_dim, lr_actor, lr_critic, hidden_width, act_continuous, use_orthogonal_init)
        lib_path = os.path.join(
            os.path.dirname(__file__),
            "hlsmodel_src",
            f"generated.nn.sim.{obs_dim}.{act_dim}.{hidden_width}.{1 if act_continuous else 0}.so"
        )

        self._init_backend()

        self._init_net_parameters(lr_critic, lr_actor, use_orthogonal_init)

        self.backward_fff = _FuncFlipFlop(self._actual_backward)
        self.step_fff = _FuncFlipFlop(self._actual_step)
        self.zero_grad_fff = _FuncFlipFlop(self._actual_zero_grad)

    def _init_backend(self):
        bitfile_path = os.path.exists(os.path.join(
            os.path.dirname(__file__),
            'hlsmodel_src',
            f'generated.system.{self.obs_dim}.{self.act_dim}.{self.hidden_width}.{1 if self.act_continuous else 0}.bit'))
        assert(os.path.exists(bitfile_path))
        pynq.PL.reset()
        self.overlay = pynq.Overlay(bitfile_path)
        self.ip_forward = self.overlay.forward
        self.ip_backward = self.overlay.backward
        self.ip_param_loader = self.overlay.param_loader
        self.ip_grad_extractor = self.overlay.grad_extractor

        self.fw_start_o    = GPIO(GPIO.get_gpio_pin(0x00), 'out')
        self.fw_done_i     = GPIO(GPIO.get_gpio_pin(0x01), 'in')
        self.fw_idle_i     = GPIO(GPIO.get_gpio_pin(0x02), 'in')

        self.bw_start_o    = GPIO(GPIO.get_gpio_pin(0x04), 'out')
        self.bw_done_i     = GPIO(GPIO.get_gpio_pin(0x05), 'in')
        self.bw_idle_i     = GPIO(GPIO.get_gpio_pin(0x06), 'in')

        self.pa_start_o    = GPIO(GPIO.get_gpio_pin(0x08), 'out')
        self.pa_done_i     = GPIO(GPIO.get_gpio_pin(0x09), 'in')
        self.pa_idle_i     = GPIO(GPIO.get_gpio_pin(0x0a), 'in')

        self.gr_start_o    = GPIO(GPIO.get_gpio_pin(0x0c), 'out')
        self.gr_done_i     = GPIO(GPIO.get_gpio_pin(0x0d), 'in')
        self.gr_idle_i     = GPIO(GPIO.get_gpio_pin(0x0e), 'in')

        self.pa_reset_o    = GPIO(GPIO.get_gpio_pin(0x10), 'out')
        self.pa_rst_busy_i = GPIO(GPIO.get_gpio_pin(0x11), 'in')

        self.gr_reset_o    = GPIO(GPIO.get_gpio_pin(0x14), 'out')
        self.gr_rst_busy_i = GPIO(GPIO.get_gpio_pin(0x15), 'in')

        self.cache_en_o    = GPIO(GPIO.get_gpio_pin(0x18), 'out')

        self.bram_sel_o    = GPIO(GPIO.get_gpio_pin(0x18), 'out')

    def _init_net_parameters(self, lr_critic, lr_actor, use_orthogonal_init):
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

        self._set_net_parameters(lr_critic=lr_critic, lr_actor=lr_actor, params=params)

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
        self.bram_sel_o.write(0)

        self.ip_param_loader.mmio.write(
            self.ip_param_loader.register_map.in_r.address,
            self.params.detach().numpy().ctypes.data_as(cm_float_p)
        )

        self.pa_start_o.write(1)
        self.pa_start_o.write(0)

        while not self.pa_idle_i.read():
            time.sleep(0)

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
        for i, o in enumerate(obs):
            maxi_x_p = o.numpy().ctypes.data_as(cm_float_p)
            maxi_y_p = holder[i].numpy().ctypes.data_as(cm_float_p)
            self.ip_forward.mmio.write(
                self.ip_forward.register_map.maxi_x.address,
                maxi_x_p)
            self.ip_forward.mmio.write(
                self.ip_forward.register_map.maxi_y.address,
                maxi_y_p)
        
            self.fw_start_o.write(1)
            self.fw_start_o.write(0)

            while not self.fw_idle_i.read():
                time.sleep(0)

        return (value.detach().requires_grad_(requires_grad),
                mu.detach().requires_grad_(requires_grad),
                sigma.detach().requires_grad_(requires_grad))

    def _actual_backward(self):
        grads: torch.Tensor = torch.concat(
            (self.mu_grad,
             self.std_grad,
             self.value_grad*self.lr_critic_modifier),
            dim=-1)

        if len(grads.shape) == 1:
            grads = grads.unsqueeze(0)

        assert(len(grads.shape) == 2)

        for g in grads:
            self.ip_backward.mmio.write(
                self.ip_backward.register_map.maxi_grad_y.address,
                g.numpy().ctypes.data_as(cm_float_p)
            )
            self.bw_start_o.write(1)
            self.bw_start_o.write(0)
            while not self.bw_idle_i.read():
                time.sleep(0)
        
    def _actual_zero_grad(self):
        self.gr_reset_o.write(1)
        self.gr_reset_o.write(0)
        while self.gr_rst_busy_i.read():
            time.sleep(0)

    def _extract_grads(self):
        grads = torch.zeros_like(self.params)
        self.bram_sel_o.write(0)
        self.ip_grad_extractor.mmio.write(
            self.ip_grad_extractor.register_map.out_r.address,
            grads.numpy().ctypes.data_as(cm_float_p)
        )
        while not self.gr_idle_i.read():
            time.sleep(0)
        self.params.grad = grads

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
