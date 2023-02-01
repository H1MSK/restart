from itertools import chain
import logging
from typing import Tuple
import torch
from torch import nn

_logger = logging.getLogger("PyModel")

def _orthogonal_init(layer, gain=1.0):
    nn.init.orthogonal_(layer.weight, gain=gain)
    nn.init.constant_(layer.bias, 0)

def _default_init(layer, gain=1.0):
    layer.weight.data.mul_(gain)
    layer.bias.data.mul_(0)

class PyModel(nn.Module):
    def __init__(self, obs_dim, act_dim, hidden_width, act_continuous, use_orthogonal_init=False) -> None:
        super().__init__()
        self.act_continuous = act_continuous

        if act_continuous:
            self.act_feat_net = nn.Sequential(
                nn.Linear(obs_dim, hidden_width),
                nn.Tanh(),
                nn.Linear(hidden_width, hidden_width),
                nn.Tanh()
            )
            self.mu_net = nn.Linear(hidden_width, act_dim)
            self.rho_net = nn.Linear(hidden_width, act_dim)

            self.actor_params = chain(
                self.act_feat_net.parameters(),
                self.mu_net.parameters(),
                self.rho_net.parameters()
            )

            if use_orthogonal_init:
                _orthogonal_init(self.act_feat_net[0])
                _orthogonal_init(self.act_feat_net[2])
                _orthogonal_init(self.mu_net, gain=0.01)
                _orthogonal_init(self.rho_net, gain=0.01)
            else:
                _default_init(self.mu_net, gain=0.1)
        else:
            raise NotImplementedError("Discrete net is not implemented yet")

        self.critic_net = nn.Sequential(
            nn.Linear(obs_dim, hidden_width),
            nn.Tanh(),
            nn.Linear(hidden_width, hidden_width),
            nn.Tanh(),
            nn.Linear(hidden_width, 1)
        )

        self.critic_params = self.critic_net.parameters()

        if use_orthogonal_init:
            _orthogonal_init(self.critic_net[0])
            _orthogonal_init(self.critic_net[2])
            _orthogonal_init(self.critic_net[4], gain=0.01)
        else:
            _default_init(self.critic_net[4], gain=0.1)
            

class PyActorCritic():
    def __init__(self,
                 obs_dim,
                 act_dim,
                 /,
                 lr_actor=1e-4,
                 lr_critic=1e-3,
                 hidden_width=64,
                 act_continuous=True,
                 use_orthogonal_init=False) -> None:
        _logger.info("Init PyActorCritic with "
            f"obs_dim={obs_dim} "
            f"act_dim={act_dim} "
            f"hidden_width={hidden_width} "
            f"act_continuous={act_continuous}")
        self.model = PyModel(
            obs_dim=obs_dim,
            act_dim=act_dim,
            hidden_width=hidden_width,
            act_continuous=act_continuous,
            use_orthogonal_init=use_orthogonal_init)
        self.act_continuous = act_continuous

        if act_continuous:
            self.optim_actor = torch.optim.Adam(
                self.model.actor_params,
                lr=lr_actor,
                eps=1e-5)
        else:
            raise NotImplementedError("Discrete net is not implemented yet")


        self.optim_critic = torch.optim.Adam(
            self.model.critic_params,
            lr=lr_critic,
            weight_decay=1e-3,
            eps=1e-5)

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
        act_feat = self.model.act_feat_net(obs)
        mu = self.model.mu_net(act_feat)
        rho = self.model.rho_net(act_feat)
        sigma = torch.exp(rho)
        return mu, sigma

    def critic(self, obs: torch.Tensor, requires_grad=False) -> torch.Tensor:
        return self.model.critic_net(obs)

    def forward(self, obs: torch.Tensor)-> Tuple[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        value = self.model.critic_net(obs)
        act_feat = self.model.act_feat_net(obs)
        mu = self.model.mu_net(act_feat)
        rho = self.model.rho_net(act_feat)
        sigma = torch.exp(rho)
        return (value, mu, sigma)

    def critic_backward(self, value_grad: torch.Tensor):
        assert(False)

    def actor_backward(self, mu_grad, std_grad):
        assert(False)

    def critic_zero_grad(self):
        self.optim_critic.zero_grad()

    def critic_step(self):
        self.optim_critic.step()

    def actor_zero_grad(self):
        self.optim_actor.zero_grad()

    def actor_step(self):
        self.optim_actor.step()

    def save(self, filename):
        sd = {
            'model':self.model.state_dict(),
            'act_continuous':self.act_continuous,
            'optims':[
                self.optim_critic.state_dict(),
                self.optim_actor.state_dict()
            ]
        }
        torch.save(sd, filename)

    def load(self, filename):
        sd = torch.load(filename)

        self.model.load_state_dict(sd['model'])
        assert(self.act_continuous == sd['act_continuous'])
        self.optim_critic.load_state_dict(sd['optims'][0])
        self.optim_actor.load_state_dict(sd['optims'][1])
