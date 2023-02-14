from abc import ABC, abstractmethod
from typing import Tuple, Type
import torch
from core.optimizations.observation_cut import ObservationCut
from core.optimizations.pca import PrincipalComponentProjection
from models.interfaces import AbstractActorCritic
from core.optimizations.observation_normalizer import ObservationNormalizer, RecordedObservationNormalizer
from core.optimizations.gae import gae
try:
    from gym import Env
except ModuleNotFoundError:
    from gymnasium import Env
import logging
import numpy as np

_logger = logging.getLogger("Agent")

class Agent(ABC):
    def __init__(
        self,
        model_class: Type[AbstractActorCritic],
        obs_dim,
        act_dim,
        /,
        lr_actor=1e-4,
        lr_critic=1e-3,
        hidden_width=64,
        act_continuous=True,
        use_orthogonal_init=False,
        use_obs_normalization=True,
        pca_dim=0,
        pca_load_file=None,
        store_obs=True,
        obs_cut_start=0,
        obs_cut_end=-1
    ) -> None:
        self.act_continuous = act_continuous
        self.distribution = (
            torch.distributions.Normal if self.act_continuous
            else torch.distributions.Categorical)
        self.critic_loss_func = torch.nn.MSELoss()

        self.obs_preprocessors = []

        cut_obs_dim = obs_dim

        if not (obs_cut_start == 0 and obs_cut_end == -1):
            self.obs_cut = ObservationCut(obs_cut_start, obs_cut_end)
            self.obs_preprocessors.append(self.obs_cut)
            if obs_cut_end >= 0:
                assert(obs_cut_start >= 0)
                cut_obs_dim = obs_cut_end - obs_cut_start
            else:
                if obs_cut_start >= 0:
                    cut_obs_dim = (obs_dim + obs_cut_end) - obs_cut_start
                else:
                    cut_obs_dim = obs_cut_end - obs_cut_start
        else:
            self.obs_cut = None
            cut_obs_dim = obs_dim

        print(obs_dim, obs_cut_start, obs_cut_end, cut_obs_dim)

        if pca_dim != 0:
            assert(0 < pca_dim <= cut_obs_dim)
            self.pca = PrincipalComponentProjection(cut_obs_dim, pca_dim)
            self.pca.load(pca_load_file)
            self.obs_preprocessors.append(self.pca)
            nn_input_dim = pca_dim
        else:
            nn_input_dim = cut_obs_dim

        self._obs_dim = obs_dim
        self._cut_dim = cut_obs_dim
        self._pca_dim = pca_dim
        self._act_dim = act_dim

        if use_obs_normalization:
            if store_obs:
                self.obs_normalizer = RecordedObservationNormalizer((nn_input_dim, ))
            else:
                self.obs_normalizer = ObservationNormalizer((nn_input_dim, ))
            self.obs_preprocessors.append(self.obs_normalizer)
        else:
            self.obs_normalizer = None

        self.obs_preprocessors = tuple(self.obs_preprocessors)

        self.ac = model_class(
            nn_input_dim,
            act_dim,
            lr_actor=lr_actor,
            lr_critic=lr_critic,
            hidden_width=hidden_width,
            act_continuous=act_continuous,
            use_orthogonal_init=use_orthogonal_init
        )

        _logger.info(
            f"Agent initialized with obs_dim={obs_dim}, act_dim={act_dim}{f', pca_dim={pca_dim}' if pca_dim > 0 else ''}")

    def obs_preprocess(self, obs):
        for f in self.obs_preprocessors:
            obs = f(obs)
        return obs

    @property
    def lr_critic(self):
        return self.ac.lr_critic

    @lr_critic.setter
    def lr_critic(self, value):
        self.ac.lr_critic = value

    @property
    def lr_actor(self):
        return self.ac.lr_actor

    @lr_actor.setter
    def lr_actor(self, value):
        self.ac.lr_actor = value

    def save(self, prefix):
        # Cut and pca are initialized using init parameters thus need not to be saved
        #
        # if self.obs_cut:
        #     self.obs_cut.save(f'{prefix}.obscut.npz')
        if self.obs_normalizer:
            self.obs_normalizer.save(f'{prefix}.obsnorm.npz')
        # if self.pca:
        #     self.pca.save(f'{prefix}.pca.npz')
        self.ac.save(f"{prefix}.model.dat")

    def load(self, prefix):
        # if self.obs_cut:
        #     self.obs_cut.load(f'{prefix}.obscut.npz')
        if self.obs_normalizer:
            self.obs_normalizer.load(f'{prefix}.obsnorm.npz')
        # if self.pca:
        #     self.pca.load(f'{prefix}.pca.npz')
        self.ac.load(f"{prefix}.model.dat")

    def forward(self, obs) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        v, mu, sigma = self.ac.forward(obs)
        pi = self.distribution(mu, sigma)
        a = pi.sample()
        logprob = pi.log_prob(a).detach()
        a = a.detach()
        return v.detach().numpy(), a.detach().numpy(), logprob.sum(-1, keepdim=True).detach().numpy()

    def get_logprob(self, obs, act):
        mu, std = self.ac.act(obs, requires_grad=False)
        pi = self.distribution(mu, std)
        return pi.log_prob(act).sum(1, keepdim=True)

    @abstractmethod
    def train_batch(self, b_obs, b_acts, b_target_logprobs, b_returns, b_advantages):
        raise NotImplementedError()

    @property
    def obs_dim(self):
        return self._obs_dim

    @property
    def act_dim(self):
        return self._act_dim
    
    @property
    def pca_dim(self):
        return self._pca_dim

    def generate_epoch(self, env: Env, epoch_size: int, max_episode_steps: int):
        memory = []
        scores = []
        steps = 0
        print(f"Sync state1:{torch.rand(1)} {np.random.rand()}")
        while steps < epoch_size:  # Horizen
            s = self.obs_preprocess(env.reset()[0])
            score = 0
            for _ in range(max_episode_steps):
                print(f"{steps}", end='\r')
                steps += 1
                # 选择行为
                v, a, p = self.forward(torch.from_numpy(
                    np.array(s).astype(np.float32)).unsqueeze(0))
                a = a[0]
                p = p[0]
                v = v[0]

                s_, r, done, _, info = env.step(a)
                s_ = self.obs_preprocess(s_)

                mask = (1-done)*1
                memory.append([s, a, r, mask, p, v])

                # print(f"Sync state2:{s_}")

                score += r
                s = s_
                if done:
                    break

            scores.append((steps, score))
        return memory, scores

    def calculate_gae(self, memory):
        rewards = torch.tensor(list(memory[:, 2]), dtype=torch.float32)
        masks = torch.tensor(list(memory[:, 3]), dtype=torch.float32)

        values = torch.tensor(np.vstack(memory[:, 5]), dtype=torch.float32)

        returns, advants = gae(len(memory), rewards, masks, values, 0.98, 0.98)
        return returns, advants


class PPOAgent(Agent):
    def __init__(
        self,
        model_class: Type[AbstractActorCritic],
        obs_dim,
        act_dim,
        /,
        lr_actor=1e-4,
        lr_critic=1e-3,
        hidden_width=64,
        act_continuous=True,
        use_orthogonal_init=False,
        use_obs_normalization=True,
        pca_dim=0,
        pca_load_file=None,
        store_obs=True,
        obs_cut_start=0,
        obs_cut_end=-1,
        epsilon=0.2
    ) -> None:
        super().__init__(model_class,
                         obs_dim, act_dim,
                         lr_actor, lr_critic,
                         hidden_width,
                         act_continuous,
                         use_orthogonal_init,
                         use_obs_normalization,
                         pca_dim,
                         pca_load_file,
                         store_obs,
                         obs_cut_start,
                         obs_cut_end)
        self.epsilon = epsilon

    def train_batch(self, b_states, b_advants, b_actions, b_returns, old_prob):
        values, mu, std = self.ac.forward(b_states, requires_grad=True)

        pi = self.distribution(mu, std)
        new_prob = pi.log_prob(b_actions).sum(1, keepdim=True)

        ratio = torch.exp(new_prob-old_prob)

        surrogate_loss = ratio*b_advants
        # values = self.ac.critic(b_states, requires_grad=True)

        critic_loss: torch.Tensor = self.critic_loss_func(values, b_returns)

        self.ac.critic_zero_grad()
        critic_loss.backward()
        if values.is_leaf:
            self.ac.critic_backward(values.grad)
        self.ac.critic_step()

        ratio = torch.clamp(ratio, 1.0-self.epsilon, 1.0+self.epsilon)

        clipped_loss = ratio * b_advants

        actor_loss = -torch.min(surrogate_loss, clipped_loss).mean()
        #actor_loss = -(surrogate_loss-beta*KL_penalty).mean()

        # self.agent.ac.optim_actor.zero_grad()
        self.ac.actor_zero_grad()
        actor_loss.backward()
        if mu.is_leaf:
            assert (std.is_leaf)
            self.ac.actor_backward(mu.grad, std.grad)
        # self.agent.ac.optim_actor.step()
        self.ac.actor_step()

        print(f"Sync state3: {actor_loss} {critic_loss}")

        return critic_loss, actor_loss
