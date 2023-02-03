from typing import Tuple
import torch
from abc import ABC, abstractmethod

class AbstractActorCritic(ABC):
    def __init__(self,
                 obs_dim,
                 act_dim,
                 /,
                 lr_actor=1e-4,
                 lr_critic=1e-3,
                 hidden_width=64,
                 act_continuous=True,
                 use_orthogonal_init=False) -> None:
        super().__init__()
        self.act_continuous = act_continuous
        self.obs_dim = obs_dim
        self.act_dim = act_dim
        self.hidden_width = hidden_width

    @property
    def lr_critic(self) -> float:
        raise NotImplementedError
    
    @lr_critic.setter
    def lr_critic(self, value: float):
        pass

    @property
    def lr_actor(self) -> float:
        pass
    
    @lr_critic.setter
    def lr_actor(self, value: float):
        pass

    @abstractmethod
    def load(self, filename: str):
        pass

    @abstractmethod
    def save(self, filename: str):
        pass

    @abstractmethod
    def act(self, obs: torch.Tensor, requires_grad=False) -> Tuple[torch.Tensor, torch.Tensor]:
        pass

    @abstractmethod
    def actor_backward(self, mu_grad, std_grad):
        pass

    @abstractmethod
    def actor_zero_grad(self):
        pass

    @abstractmethod
    def actor_step(self):
        pass

    @abstractmethod
    def critic(self, obs: torch.Tensor, requires_grad=False) -> torch.Tensor:
        pass

    @abstractmethod
    def critic_backward(self, value_grad: torch.Tensor):
        pass

    @abstractmethod
    def critic_zero_grad(self):
        pass

    @abstractmethod
    def critic_step(self):
        pass
