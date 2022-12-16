from typing import List, Tuple, Type, Union
import torch
from models.cmodel import CActirCritic
from models.pymodel import PyActorCritic
from py.optimizations.observation_normalizer import ObservationNormalizer
from py.rollout_buffer import RolloutBuffer, gae
from gym import Env
import logging
import numpy as np


class Agent():
    def __init__(
        self,
        model_class: Union[Type[PyActorCritic], Type[CActirCritic]],
        obs_dim,
        act_dim,
        /,
        lr_actor=1e-4,
        lr_critic=1e-3,
        hidden_width=64,
        act_continuous=True
    ) -> None:
        self.act_continuous = act_continuous
        self.distribution = (
            torch.distributions.Normal if self.act_continuous
            else torch.distributions.Categorical)
        self.critic_loss_func = torch.nn.MSELoss()

        self.ac = model_class(
            obs_dim,
            act_dim,
            lr_actor=lr_actor,
            lr_critic=lr_critic,
            hidden_width=hidden_width,
            act_continuous=act_continuous
        )

        self._obs_dim = obs_dim
        self._act_dim = act_dim

        self.obs_normalizer = ObservationNormalizer((obs_dim, ))

        logging.info(
            f"Agent initialized with obs_dim={obs_dim}, act_dim={act_dim}")

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
        self.obs_normalizer.save(f'{prefix}.obsnorm.npz')
        self.ac.save(f"{prefix}.model.dat")

    def load(self, prefix):
        self.obs_normalizer.load(f'{prefix}.obsnorm.npz')
        self.ac.load(f"{prefix}.model.dat")

    def choose_action(self, obs)-> Tuple[np.ndarray, np.ndarray]:
        mu, sigma = self.ac.act(obs, requires_grad=False)
        pi = self.distribution(mu, sigma)
        a = pi.sample()
        logprob = pi.log_prob(a).detach()
        a = a.detach()
        return a.numpy(), logprob.sum(dim=1, keepdim=True).detach()

    def get_logprob(self, obs, act):
        mu, std = self.ac.act(obs, requires_grad=False)
        pi = self.distribution(mu, std)
        return pi.log_prob(act).sum(1, keepdim=True)

    def predict(self, obs):
        value, pi = self.ac.forward(obs)
        if self.act_continuous:
            mu, rho = pi
            sigma = torch.exp(rho)
            distrib = self.distribution(mu, sigma)
            return value.item(), distrib
        else:
            raise NotImplementedError()

    def train_batch(self, b_obs, b_acts, b_target_logprobs, b_returns, b_advantages):
        raise NotImplementedError()

    @property
    def obs_dim(self):
        return self._obs_dim

    @property
    def act_dim(self):
        return self._act_dim

    def generate_rb(self, env: Env, stop_when_terminated=False, max_steps=2048, max_episode_steps=10000, discount=0.99, lambda_gae=0.9, training=False):
        rb = RolloutBuffer()

        self.obs_normalizer.update_normalizer = training

        rewards: List[Tuple[int, float]] = []
        while rb.n < max_steps:
            obs, _ = env.reset()
            obs = self.obs_normalizer(obs)
            obs = torch.tensor(obs, dtype=torch.float32)
            episode_reward = 0
            for _ in range(max_episode_steps):
                value, distrib = self.predict(obs.unsqueeze(0))
                act = distrib.sample()
                logprob = distrib.log_prob(act).detach()
                next_obs, reward, terminated, _, __ = env.step(
                    act[0].detach().numpy())
                next_obs = self.obs_normalizer(next_obs)
                episode_reward += reward
                rb.append(obs, act, reward, value, logprob.sum(
                    1, keepdim=True), terminated)
                if terminated:
                    break
                obs = torch.tensor(next_obs, dtype=torch.float32)

        rewards.append((rb.n, episode_reward))

        return rb, rewards

    def generate_epoch(self, env: Env, epoch_size: int, max_episode_steps: int):
        episodes = 0

        memory = []
        scores = []
        steps = 0
        print(f"Sync state1:{torch.rand(1)} {np.random.rand()}")
        while steps < epoch_size:  # Horizen
            episodes += 1
            s = self.obs_normalizer(env.reset()[0])
            score = 0
            for _ in range(max_episode_steps):
                print(f"{steps}", end='\r')
                steps += 1
                # 选择行为
                a, p = self.choose_action(torch.from_numpy(
                    np.array(s).astype(np.float32)).unsqueeze(0))
                a = a[0]
                p = p[0]

                s_, r, done, _, info = env.step(a)
                s_ = self.obs_normalizer(s_)

                mask = (1-done)*1
                memory.append([s, a, r, mask, p])

                # print(f"Sync state2:{s_}")

                score += r
                s = s_
                if done:
                    break

            scores.append((steps, score))
        return memory, scores

    def calculate_gae(self, memory, states):
        rewards = torch.tensor(list(memory[:, 2]), dtype=torch.float32)
        masks = torch.tensor(list(memory[:, 3]), dtype=torch.float32)

        values = self.ac.critic(states).detach()

        returns, advants = gae(len(memory), rewards, masks, values, 0.98, 0.98)
        return returns, advants


class PPOAgent(Agent):
    def __init__(
        self,
        model_class: Type[PyActorCritic],
        obs_dim,
        act_dim,
        /,
        lr_actor=1e-4,
        lr_critic=1e-3,
        hidden_width=64,
        act_continuous=True,
        epsilon=0.2
    ) -> None:
        super().__init__(model_class, obs_dim, act_dim, lr_actor,
                         lr_critic, hidden_width, act_continuous)
        self.epsilon = epsilon

    def train_batch(self, b_states, b_advants, b_actions, b_returns, old_prob):
        mu, std = self.ac.act(b_states, requires_grad=True)

        pi = self.distribution(mu, std)
        new_prob = pi.log_prob(b_actions).sum(1, keepdim=True)

        ratio = torch.exp(new_prob-old_prob)

        surrogate_loss = ratio*b_advants
        values = self.ac.critic(b_states, requires_grad=True)

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
