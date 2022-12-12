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

class CActirCritic():
    def __init__(self,
                 obs_dim,
                 act_dim,
                 /,
                 lr_actor=1e-4,
                 lr_critic=1e-3,
                 hidden_width=64,
                 act_continuous=True) -> None:
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

        self._init_net_parameters(lr_critic, lr_actor)

    def _init_functions(self):
        self.get_net_parameters = self.model.get_net_parameters
        self.get_net_parameters.argtypes = (
            c_int_p, c_int_p, c_int_p, c_int_p, c_int_p, c_int_p)

        self.actor_arr_top = self.model.actor_arr_top
        self.actor_arr_top.argtypes = (
            c_int, c_float_p, c_float_p, c_float_p, c_float_p, c_float_p)

        self.critic_arr_top = self.model.critic_arr_top
        self.critic_arr_top.argtypes = (
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

    def _set_net_parameters(self, /, lr_critic, lr_actor, cparams, aparams):
        self.cparams = cparams.detach().requires_grad_()
        self.aparams = aparams.detach().requires_grad_()

        if self.cparams.dtype != torch_cm_float:
            self.cparams = torch.tensor(self.cparams, dtype=torch_cm_float)
        if self.aparams.dtype != torch_cm_float:
            self.aparams = torch.tensor(self.aparams, dtype=torch_cm_float)

        self.cparams.requires_grad_(True)
        self.aparams.requires_grad_(True)

        assert(len(self.cparams) == self.critic_param_size)
        assert(len(self.aparams) == self.actor_param_size)

        self._apply_actor_params()

        self._apply_critic_params()

        if self.act_continuous:
            self.optim_actor = torch.optim.Adam(
                [self.aparams],
                lr=lr_actor,
                eps=1e-5)
        else:
            raise NotImplementedError("Discrete net is not implemented yet")

        self.optim_critic = torch.optim.Adam(
            [self.cparams],
            lr=lr_critic,
            weight_decay=1e-3,
            eps=1e-5)

    def _init_net_parameters(self, lr_critic, lr_actor):
        pymodel = PyModel(
            self.obs_dim,
            self.act_dim,
            self.hidden_width,
            self.act_continuous)

        cparams = torch.concat([x.reshape((-1, )) for x in pymodel.critic_params])
        aparams = torch.concat([x.reshape((-1, )) for x in pymodel.actor_params])

        del pymodel

        self._set_net_parameters(lr_actor=lr_actor, lr_critic=lr_critic, cparams=cparams, aparams=aparams)

        _logger.debug(f"Init param size: critic={len(self.cparams)} actor={len(self.aparams)}")

    def _apply_critic_params(self):
        self.critic_arr_top(NN_OP_LoadParam,
            self.cparams.detach().numpy().ctypes.data_as(cm_float_p),  # in_param
            c_float_p(),                                    # out_grad
            c_float_p(),                                    # in_x
            c_float_p(),                                    # in_grad_y
            c_float_p(),                                    # out_y
        )

    def _apply_actor_params(self):
        self.actor_arr_top(NN_OP_LoadParam,
            self.aparams.detach().numpy().ctypes.data_as(cm_float_p),  # in_param
            c_float_p(),                                    # out_grad
            c_float_p(),                                    # in_x
            c_float_p(),                                    # in_grad_y
            c_float_p(),                                    # out_y
        )

    @property
    def lr_critic(self):
        return self.optim_critic.param_groups[0]['lr']
    
    @lr_critic.setter
    def lr_critic(self, value):
        for p in self.optim_critic.param_groups:
            p['lr'] = value

    @property
    def lr_actor(self):
        return self.optim_actor.param_groups[0]['lr']
    
    @lr_actor.setter
    def lr_actor(self, value):
        for p in self.optim_actor.param_groups:
            p['lr'] = value

    def act(self, obs: torch.Tensor, requires_grad=False) -> Tuple[torch.Tensor, torch.Tensor]:
        assert(self.act_continuous)
        mu = torch.zeros((len(obs), self.act_dim), dtype=torch_cm_float)
        sigma = torch.zeros((len(obs), self.act_dim), dtype=torch_cm_float)
        for i, o in enumerate(obs):
            mu_and_sigma = torch.zeros((self.act_dim*2, ), dtype=torch_cm_float)

            self.actor_arr_top(
                NN_OP_ForwardWithCache if requires_grad else NN_OP_Forward,
                c_float_p(),                                        # in_param
                c_float_p(),                                        # out_grad
                o.numpy().ctypes.data_as(cm_float_p),               # in_x
                c_float_p(),                                        # in_grad_y
                mu_and_sigma.numpy().ctypes.data_as(cm_float_p),    # out_y
            )

            mu[i, :] = mu_and_sigma[:self.act_dim]
            sigma[i, :] = mu_and_sigma[self.act_dim:]

        return mu.requires_grad_(requires_grad), sigma.requires_grad_(requires_grad)

    def critic(self, obs: torch.Tensor, requires_grad=False) -> torch.Tensor:
        values = torch.zeros((len(obs), 1), dtype=torch_cm_float)

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

        return values.requires_grad_(requires_grad)

    def critic_backward(self, value_grad):
        for g in value_grad:
            self.critic_arr_top(
                NN_OP_Backward,
                c_float_p(),                                    # in_param
                c_float_p(),                                    # out_grad
                c_float_p(),                                    # in_x
                g.numpy().ctypes.data_as(cm_float_p),           # in_grad_y
                c_float_p(),                                    # out_y
            )

    def actor_backward(self, mu_grad, std_grad):
        grads = torch.concat((mu_grad, std_grad), dim=-1)
        for g in grads:
            self.actor_arr_top(
                NN_OP_Backward,
                c_float_p(),                                    # in_param
                c_float_p(),                                    # out_grad
                c_float_p(),                                    # in_x
                g.numpy().ctypes.data_as(cm_float_p),           # in_grad_y
                c_float_p(),                                    # out_y
            )

    def actor_zero_grad(self):
        dummy = torch.zeros_like(self.aparams)
        self.actor_arr_top(
            NN_OP_DumpGradAndZero,
            c_float_p(),                                        # in_param
            dummy.numpy().ctypes.data_as(cm_float_p),           # out_grad
            c_float_p(),                                        # in_x
            c_float_p(),                                        # in_grad_y
            c_float_p(),                                        # out_y
        )

    def critic_zero_grad(self):
        dummy = torch.zeros_like(self.cparams)
        self.critic_arr_top(
            NN_OP_DumpGradAndZero,
            c_float_p(),                                        # in_param
            dummy.numpy().ctypes.data_as(cm_float_p),           # out_grad
            c_float_p(),                                        # in_x
            c_float_p(),                                        # in_grad_y
            c_float_p(),                                        # out_y
        )

    def actor_step(self):
        grads = torch.zeros_like(self.aparams)
        self.actor_arr_top(
            NN_OP_DumpGradAndZero,
            c_float_p(),                                    # in_param
            grads.numpy().ctypes.data_as(cm_float_p),       # out_grad
            c_float_p(),                                    # in_x
            c_float_p(),                                    # in_grad_y
            c_float_p(),                                    # out_y
        )
        self.aparams.grad=grads
        self.optim_actor.step()
        self._apply_actor_params()

    def critic_step(self):
        grads = torch.zeros_like(self.cparams)
        self.critic_arr_top(
            NN_OP_DumpGradAndZero,
            c_float_p(),                                    # in_param
            grads.numpy().ctypes.data_as(cm_float_p),       # out_grad
            c_float_p(),                                    # in_x
            c_float_p(),                                    # in_grad_y
            c_float_p(),                                    # out_y
        )
        self.cparams.grad=grads
        self.optim_critic.step()
        self._apply_critic_params()

    def save(self, filename):
        sd = {
            'model':[self.cparams, self.aparams],
            'act_continuous':self.act_continuous,
            'optims':[
                self.optim_critic.state_dict(),
                self.optim_actor.state_dict()
            ]
        }
        torch.save(sd, filename)

    def load(self, filename):
        sd = torch.load(filename)

        cparams = sd['model'][0]
        aparams = sd['model'][1]
        self._set_net_parameters(
            lr_critic=self.lr_critic,
            lr_actor=self.lr_actor,
            cparams=cparams,
            aparams=aparams)
        assert(self.act_continuous == sd['act_continuous'])
        self.optim_critic.load_state_dict(sd['optims'][0])
        self.optim_actor.load_state_dict(sd['optims'][1])
