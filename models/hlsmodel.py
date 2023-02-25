from itertools import chain
import os
from models.interfaces import AbstractActorCritic
import torch
import numpy as np
from typing import Callable, Tuple
import pynq
from pynq import GPIO
import time
import logging
from cm_type import get_float_pointer, torch_cm_float, np_cm_float

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

        self.backward_fff = _FuncFlipFlop(self._actual_backward)
        self.step_fff = _FuncFlipFlop(self._actual_step)
        self.zero_grad_fff = _FuncFlipFlop(self._actual_zero_grad)

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

        # self.cache_en_o    = GPIO(GPIO.get_gpio_pin(0x18), 'out')

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
        self.lr_actor = lr_actor

        self.params = pynq.allocate(params.shape, dtype=np_cm_float)
        np.copyto(self.params, params.detach().numpy(), casting='same_kind')
        self.grads = pynq.allocate(params.shape, dtype=np_cm_float)
        self.params_tensor = torch.from_numpy(self.params).requires_grad_(True)

        self._apply_params()

        assert(self.act_continuous)
        self.optim = torch.optim.Adam(
            [self.params_tensor],
            lr=lr_actor,
            eps=1e-5
        )

    def _apply_params(self):
        _logger.info("Parameters syncing out...")
        self.bram_sel_o.write(0)

        self.params.sync_to_device()

        while not self.ip_param_loader.register_map.CTRL.AP_IDLE:
            pass

        self.ip_param_loader.register_map.in_r=self.params.device_address

        self.ip_param_loader.register_map.CTRL.AP_START=1

        while not (x := self.ip_param_loader.register_map.CTRL).AP_DONE and not x.AP_IDLE:
            pass

        _logger.info("Parameters syncing finished!")

    @property
    def lr_critic(self):
        return self.lr_actor * self.lr_critic_modifier
    
    @lr_critic.setter
    def lr_critic(self, value):
        self.lr_critic_modifier = value / self.lr_actor

    def forward(self, obs: torch.Tensor, requires_grad=False) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        holder_x = pynq.allocate((len(obs), self.obs_dim), dtype=np_cm_float)
        holder_y = pynq.allocate((len(obs), self.act_dim * 2 + 1), dtype=np_cm_float)
        np.copyto(holder_x, obs.numpy())
        self.bram_sel_o.write(1)

        while not self.ip_forward.register_map.CTRL.AP_IDLE:
            pass

        holder_x.sync_to_device()

        self.ip_forward.register_map.n=len(obs)
        self.ip_forward.register_map.cache_en = (1 if requires_grad else 0)
        self.ip_forward.register_map.maxi_x=holder_x.device_address
        self.ip_forward.register_map.maxi_y=holder_y.device_address
        self.ip_forward.register_map.CTRL.AP_START = 1

        while not (x:=self.ip_forward.register_map.CTRL).AP_IDLE and not x.AP_DONE:
            pass

        holder_y.sync_from_device()

        return (torch.from_numpy(holder_y[:, self.act_dim*2:]).requires_grad_(requires_grad),
                torch.from_numpy(holder_y[:, :self.act_dim]).requires_grad_(requires_grad),
                torch.from_numpy(holder_y[:, self.act_dim:self.act_dim*2]).requires_grad_(requires_grad))

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

        holder = pynq.allocate(grads.shape, dtype=np_cm_float)
        np.copyto(holder, grads)

        while not self.ip_backward.register_map.CTRL.AP_IDLE:
            pass

        holder.sync_to_device()

        self.ip_backward.register_map.n = len(grads)
        self.ip_backward.register_map.maxi_grad_y=holder.device_address
        self.ip_backward.register_map.CTRL.AP_START=1

        while not (x:=self.ip_backward.register_map.CTRL).AP_IDLE and not x.AP_DONE:
            pass

    def _actual_zero_grad(self):
        self.gr_reset_o.write(1)
        # TODO: test this
        while not self.gr_rst_busy_i.read():
            pass
        self.gr_reset_o.write(0)
        while self.gr_rst_busy_i.read():
            pass

    def _extract_grads(self):
        self.bram_sel_o.write(0)

        while not self.ip_grad_extractor.register_map.CTRL.AP_IDLE:
            pass

        self.grads.sync_to_device()

        self.ip_grad_extractor.register_map.out_r=self.grads.device_address

        self.ip_grad_extractor.register_map.CTRL.AP_START=1
        while not (x := self.ip_grad_extractor.register_map.CTRL).AP_DONE and not x.AP_IDLE:
            pass

        self.grads.sync_from_device()
    
    def _actual_step(self):
        self._extract_grads()
        self.params_tensor.grad = torch.from_numpy(self.grads)
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
