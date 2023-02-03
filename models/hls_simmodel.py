from itertools import chain
import os
from models.interfaces import AbstractActorCritic
from ctypes import CDLL, c_float, c_bool, c_int, POINTER
import torch
from typing import Callable, Tuple

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
        self.model = CDLL(lib_path)
        
        self.net_load_param = self.model.load_param
        self.net_load_param.argtypes = (cm_float_p, )

        self.net_extract_grad = self.model.extract_grad
        self.net_extract_grad.argtypes = (cm_float_p, )

        self.net_zero_grad = self.model.zero_grad

        self.net_forward = self.model.forward
        self.net_forward.argtypes = (c_bool, cm_float_p, cm_float_p)

        self.net_backward = self.model.backward
        self.net_backward.argtypes = (cm_float_p, )

        self.backward_fff = _FuncFlipFlop(self._actual_backward)
        self.step_fff = _FuncFlipFlop(self._actual_step)
        self.zero_grad_fff = _FuncFlipFlop(self._actual_zero_grad)

        self._init_net_parameters(lr_critic, lr_actor, use_orthogonal_init)

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

        del pymodel

        self._set_net_parameters(lr_critic=lr_critic, lr_actor=lr_actor, params=params)

    def _set_net_parameters(self, /, lr_critic: float, lr_actor: float, params: torch.Tensor):
        self.lr_critic_modifier = lr_critic / lr_actor

        if params.dtype != torch_cm_float:
            params = torch.tensor(params, dtype=torch_cm_float)
        self.params: torch.Tensor = params.detach().requires_grad_(True)

        self._apply_params()

        assert(self.act_continuous)
        self.optim = torch.optim.Adam(
            [self.params],
            lr=lr_actor,
            eps=1e-5
        )

    def _apply_params(self):
        self.net_load_param(
            self.params.detach().numpy().ctypes.data_as(cm_float_p)
        )

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
        mu = torch.zeros((len(obs), self.act_dim), dtype=torch_cm_float)
        sigma = torch.zeros((len(obs), self.act_dim), dtype=torch_cm_float)
        value = torch.zeros((len(obs), 1), dtype=torch_cm_float)

        holder = torch.zeros((self.act_dim * 2 + 1), dtype=torch_cm_float)

        for i, o in enumerate(obs):
            self.net_forward(
                c_bool(requires_grad),
                o.numpy().ctypes.data_as(cm_float_p),
                holder.numpy().ctypes.data_as(cm_float_p)
            )
            mu[i] = holder[0:self.act_dim].clone().detach()
            sigma[i] = holder[self.act_dim:self.act_dim*2].clone().detach()
            value[i] = holder[self.act_dim*2].clone().detach()

        return (value.requires_grad_(requires_grad),
                mu.requires_grad_(requires_grad),
                sigma.requires_grad_(requires_grad))

    def act(self, obs: torch.Tensor, requires_grad=False) -> Tuple[torch.Tensor, torch.Tensor]:
        return self.forward(obs, requires_grad)[1:]

    def critic(self, obs: torch.Tensor, requires_grad=False) -> torch.Tensor:
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

        for g in grads:
            self.net_backward(
                g.numpy().ctypes.data_as(cm_float_p)
            )
        
    def _actual_zero_grad(self):
        self.net_zero_grad()

    def _extract_grads(self):
        grads = torch.zeros_like(self.params)
        self.net_extract_grad(
            grads.numpy().ctypes.data_as(cm_float_p)
        )
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
