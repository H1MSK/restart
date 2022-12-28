from ctypes import CDLL, c_float, POINTER, c_int, pointer
import logging
from typing import Tuple
import torch

from models.pymodel import PyModel


c_int_p = POINTER(c_int)
c_float_p = POINTER(c_float)

cm_float = c_float
torch_cm_float = torch.float32
cm_float_p = c_float_p

NN_OP_None              = 0x00
NN_OP_LoadParam         = 0x01
NN_OP_DumpGradAndZero   = 0x02
NN_OP_Forward           = 0x10
NN_OP_ForwardWithCache  = 0x20
NN_OP_Backward          = 0x40

_logger = logging.getLogger("CActirCritic")

class UniCActirCritic():
    def __init__(self,
                 obs_dim,
                 act_dim,
                 /,
                 lr_actor=1e-4,
                 lr_critic=1e-3,
                 hidden_width=64,
                 act_continuous=True,
                 use_orthogonal_init=False) -> None:
        _logger.info("Init CActorCritic with "
            f"obs_dim={obs_dim} "
            f"act_dim={act_dim} "
            f"hidden_width={hidden_width} "
            f"act_continuous={act_continuous}")
            
        self.model = CDLL("models/build/libcmodel_"
            f"{obs_dim}_{act_dim}_{hidden_width}_"
            f"{1 if act_continuous else 0}.so")

        self._init_functions()

        self._check_and_init_hyperparams(
            obs_dim, act_dim, hidden_width, act_continuous)

        self._init_net_parameters(lr_critic, lr_actor, use_orthogonal_init)

        self.value_grad_tag = 0
        self.actor_grad_tag = 0
        self.value_step_tag = 0
        self.actor_step_tag = 0

    def _init_functions(self):
        self.get_net_parameters = self.model.get_net_parameters
        self.get_net_parameters.argtypes = (
            c_int_p, c_int_p, c_int_p, c_int_p, c_int_p, c_int_p)

        self.uni_arr_top = self.model.actor_arr_top
        self.uni_arr_top.argtypes = (
            c_int, c_float_p, c_float_p, c_float_p, c_float_p, c_float_p)

    def _check_and_init_hyperparams(
            self, obs_dim, act_dim, hidden_width, act_continuous):
        c_obs = c_int()
        c_act = c_int()
        c_hidden = c_int()
        c_aparam = c_int()
        c_cparam = c_int()
        c_act_continuous = c_int()

        self.get_net_parameters(
            pointer(c_obs),
            pointer(c_act),
            pointer(c_hidden),
            pointer(c_aparam),
            pointer(c_cparam),
            pointer(c_act_continuous)
        )

        _logger.debug("Backend returns param: "
              f"obs_dim={c_obs.value} "
              f"act_dim={c_act.value} "
              f"hidden_width={c_hidden.value} "
              f"actor_param_len={c_aparam.value} "
              f"critic_param_len={c_cparam.value} "
              f"act_continuous={c_act_continuous.value}")

        assert(obs_dim == c_obs.value)
        assert(act_dim == c_act.value)
        assert(hidden_width == c_hidden.value)
        assert(c_act_continuous.value == (1 if act_continuous else 0))

        self.actor_param_size = c_aparam.value
        self.critic_param_size = c_cparam.value
        self.act_continuous = act_continuous
        self.obs_dim = obs_dim
        self.act_dim = act_dim
        self.hidden_width = hidden_width

    def _set_net_parameters(self, /, lr_critic, lr_actor, params):
        self.params = params.detach()

        if self.params.dtype != torch_cm_float:
            self.params = torch.tensor(self.params, dtype=torch_cm_float)

        self.params.requires_grad_(True)

        assert(len(self.params) == self.actor_param_size + self.critic_param_size)

        assert(lr_critic == lr_actor)

        self._apply_params()

        self.optim = torch.optim.Adam(
            [self.params],
            lr=lr_actor,
            eps=1e-5)


    def _init_net_parameters(self, lr_critic, lr_actor, use_orthogonal_init):
        pymodel = PyModel(
            self.obs_dim,
            self.act_dim,
            self.hidden_width,
            self.act_continuous,
            use_orthogonal_init)

        cparams = torch.concat([x.reshape((-1, )) for x in pymodel.critic_params])
        aparams = torch.concat([x.reshape((-1, )) for x in pymodel.actor_params])
        params = torch.concat([cparams, aparams], dim=-1)

        del pymodel

        self._set_net_parameters(lr_actor=lr_actor, lr_critic=lr_critic, params=params)

        _logger.debug(f"Init param size: critic={len(self.cparams)} actor={len(self.aparams)}")

    def _apply_params(self):
        self.uni_arr_top(NN_OP_LoadParam,
            self.params.detach().numpy().ctypes.data_as(cm_float_p),  # in_param
            c_float_p(),                                    # out_grad
            c_float_p(),                                    # in_x
            c_float_p(),                                    # in_grad_y
            c_float_p(),                                    # out_y
        )

    @property
    def lr_critic(self):
        return self.optim.param_groups[0]['lr']
    
    @lr_critic.setter
    def lr_critic(self, value):
        for p in self.optim.param_groups:
            p['lr'] = value

    @property
    def lr_actor(self):
        return self.optim.param_groups[0]['lr']
    
    @lr_actor.setter
    def lr_actor(self, value):
        for p in self.optim.param_groups:
            p['lr'] = value

    def forward(self, obs: torch.Tensor, requires_grad=False) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        assert(self.act_continuous)
        values = torch.zeros((len(obs), 1), dtype=torch_cm_float)
        mu = torch.zeros((len(obs), self.act_dim), dtype=torch_cm_float)
        sigma = torch.zeros((len(obs), self.act_dim), dtype=torch_cm_float)
        out = torch.zeros((self.act_dim*2+1, ), dtype=torch_cm_float)
        for i, o in enumerate(obs):

            self.actor_arr_top(
                NN_OP_ForwardWithCache if requires_grad else NN_OP_Forward,
                c_float_p(),                                        # in_param
                c_float_p(),                                        # out_grad
                o.numpy().ctypes.data_as(cm_float_p),               # in_x
                c_float_p(),                                        # in_grad_y
                out.numpy().ctypes.data_as(cm_float_p),             # out_y
            )

            values[i, :] = out[0]
            mu[i, :] = out[1:1+self.act_dim]
            sigma[i, :] = out[self.act_dim+1:]

        for i, o in enumerate(obs):
            v = torch.zeros((1, ), dtype=torch_cm_float)
            self.critic_arr_top(
                NN_OP_ForwardWithCache if requires_grad else NN_OP_Forward,
                c_float_p(),                                        # in_param
                c_float_p(),                                        # out_grad
                o.numpy().ctypes.data_as(cm_float_p),               # in_x
                c_float_p(),                                        # in_grad_y
                v.numpy().ctypes.data_as(cm_float_p),               # out_y
            )
            values[i, :] = v

        return values.requires_grad_(requires_grad), mu.requires_grad_(requires_grad), sigma.requires_grad_(requires_grad)


    def act(self, obs: torch.Tensor, requires_grad=False) -> Tuple[torch.Tensor, torch.Tensor]:
        v, m, s = self.forward(obs, requires_grad)
        return m, s

    def critic(self, obs: torch.Tensor, requires_grad=False) -> torch.Tensor:
        v, m, s = self.forward(obs, requires_grad)
        return v

    def _net_backward(self, grads):
        for g in grads:
            self.uni_arr_top(
                NN_OP_Backward,
                c_float_p(),                                    # in_param
                c_float_p(),                                    # out_grad
                c_float_p(),                                    # in_x
                g.numpy().ctypes.data_as(cm_float_p),           # in_grad_y
                c_float_p(),                                    # out_y
            )

    def critic_backward(self, value_grad):
        self.value_grad = value_grad
        self.value_grad_tag += 1
        if self.value_grad_tag == self.actor_grad_tag:
            grad = torch.concat((self.value_grad, self.mu_grad, self.std_grad), dim=-1)
            self._net_backward(grad)

    def actor_backward(self, mu_grad, std_grad):
        self.mu_grad = mu_grad
        self.std_grad = std_grad
        self.actor_grad_tag += 1
        if self.value_grad_tag == self.actor_grad_tag:
            grad = torch.concat((self.value_grad, self.mu_grad, self.std_grad), dim=-1)
            self._net_backward(grad)

    def actor_zero_grad(self):
        return

    def critic_zero_grad(self):
        return

    def _net_step(self):
        grads = torch.zeros_like(self.params)
        self.uni_arr_top(
            NN_OP_DumpGradAndZero,
            c_float_p(),                                    # in_param
            grads.numpy().ctypes.data_as(cm_float_p),       # out_grad
            c_float_p(),                                    # in_x
            c_float_p(),                                    # in_grad_y
            c_float_p(),                                    # out_y
        )
        self.params.grad=grads
        self.optim.step()
        self._apply_params()

    def actor_step(self):
        self.actor_step_tag += 1
        if self.value_step_tag == self.actor_step_tag:
            self._net_step()

    def critic_step(self):
        self.value_step_tag += 1
        if self.value_step_tag == self.actor_step_tag:
            self._net_step()

    def save(self, filename):
        sd = {
            'model':self.params,
            'act_continuous':self.act_continuous,
            'optims':self.optim,
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
        self.optim.load_state_dict(sd['optims'])
