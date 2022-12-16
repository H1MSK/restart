import math
import os
from typing import List, Literal, Optional, Tuple, Type, Union
from gym import Env
import torch
from torch.utils.tensorboard.writer import SummaryWriter
from models.pymodel import PyActorCritic
import configparser
from param_choice import *
from py.agent import Agent
import imageio
import numpy as np
import logging

from py.rollout_buffer import RolloutBuffer, gae

class TrainManager:
    def __init__(self, /,
            session_name: Optional[str] = None,
            model_name: str = None,
            agent_name: str = None,
            env_name: str = None,
            lr_actor=1e-4,
            lr_critic=1e-3,
            hidden_width=64,
            seed=0) -> None:

        if not os.path.exists('./run'):
            os.mkdir('./run')
        elif not os.path.isdir('./run'):
            raise OSError("./run is not directory")

        if session_name == None:
            assert(model_name in model_choices.keys() and
                   agent_name in agent_choices.keys() and
                   env_name in env_choices.keys() and
                   lr_actor > 0 and
                   lr_critic > 0 and
                   isinstance(hidden_width, int))
            iter = 1
            while os.path.exists(f'./run/session_{iter}'):
                iter += 1
            session_name=f'session_{iter}'
            os.mkdir(f'./run/{session_name}')
            self.conf = configparser.ConfigParser()
            self.conf.add_section('default')
            self.conf.set('default', 'model', model_name)
            self.conf.set('default', 'agent', agent_name)
            self.conf.set('default', 'env', env_name)
            self.conf.set('default', 'lr_actor', str(lr_actor))
            self.conf.set('default', 'lr_critic', str(lr_critic))
            self.conf.set('default', 'hidden_width', str(hidden_width))
            self.conf.set('default', 'seed', str(seed))
            with open(f'./run/{session_name}/conf.ini', 'w') as f:
                self.conf.write(f)
            need_load = False
        else:
            if not os.path.isdir(f'./run/{session_name}'):
                raise ValueError(f'Session(./run/{session_name}) not found')
            elif not os.path.isfile(f'./run/{session_name}/conf.ini'):
                raise ValueError(f'Config for session(./run/{session_name}/conf.ini) not found')
            self.conf = configparser.ConfigParser()
            self.conf.read(f'./run/{session_name}/conf.ini')
            need_load = True
            model_name = self.conf.get('default', 'model')
            agent_name = self.conf.get('default', 'agent')
            env_name = self.conf.get('default', 'env')
            lr_actor = float(self.conf.get('default', 'lr_actor'))
            lr_critic = float(self.conf.get('default', 'lr_critic'))
            hidden_width = int(self.conf.get('default', 'hidden_width'))
            seed = int(self.conf.get('default', 'seed'))
            assert(model_name in model_choices.keys() and
                   agent_name in agent_choices.keys() and
                   env_name in env_choices.keys() and
                   lr_actor > 0 and
                   lr_critic > 0 and
                   isinstance(hidden_width, int))


        self.train_env = env_choices[env_name]()
        self.test_env = env_choices[env_name](render_mode='rgb_array_list')

        if seed != 0:
            self.train_env.action_space.seed(seed)
            self.test_env.action_space.seed(seed)
            torch.manual_seed(seed)
            np.random.seed(seed)
            self.train_env.reset(seed=seed)
            self.test_env.reset(seed=seed)
            logging.info(f"Set seed to {seed}")

        act_continuous = not isinstance(self.train_env.action_space, gym.spaces.discrete.Discrete)
        obs_dim = self.train_env.observation_space.shape[0]
        if act_continuous:
            act_dim = self.train_env.action_space.shape[0]
        else:
            act_dim = self.train_env.action_space.n

        self.agent = agent_choices[agent_name](
            model_choices[model_name],
            obs_dim,
            act_dim,
            lr_actor=lr_actor,
            lr_critic=lr_critic,
            hidden_width=hidden_width,
            act_continuous=act_continuous,
            epsilon=0.2)
        self.writer = SummaryWriter(f'./run/{session_name}/logs')
        self.train_count = 0
        self.test_count = 0

        self.session_name = session_name

        if need_load:
            self.load('last')

        logging.info(f"Session={session_name}, log=./run/{session_name}/logs")

    def train_epoch(self, epoch_size=2048, max_episode_steps=10000, epoch=1, batch_size=64):
        # memory, scores = self.generate_epoch(epoch_size, max_episode_steps)
        memory, scores = self.agent.generate_epoch(
            self.train_env,
            epoch_size=epoch_size,
            max_episode_steps=max_episode_steps)

        for step, score in scores:
            self.writer.add_scalar("Episode reward", score, batch_size * self.train_count + step)
        score_avg = sum(i[1] for i in scores) / len(scores)

        memory = np.array(memory, dtype=object)
        states = torch.tensor(np.vstack(memory[:,0]),dtype=torch.float32)

        actions = torch.tensor(np.vstack(memory[:,1]),dtype=torch.float32)
        returns, advants = self.agent.calculate_gae(memory, states)

        # old_f = self.agent.ac.model.act_feat_net(states)
        # old_mu = self.agent.ac.model.mu_net(old_f)
        # old_rho = self.agent.ac.model.rho_net(old_f)
        # old_std = torch.exp(old_rho)
        # old_mu, old_std = self.agent.ac.act(states)
        
        # pi = self.agent.distribution(old_mu,old_std)

        # old_log_prob = pi.log_prob(actions).sum(1,keepdim=True)
        old_log_prob = self.agent.get_logprob(states, actions)

        n = len(states)
        arr = np.arange(n)
        for e in range(epoch):
            np.random.shuffle(arr)
            for i in range(n//batch_size):
                b_index = arr[batch_size*i:batch_size*(i+1)]
                b_states = states[b_index]
                b_advants = advants[b_index]
                b_actions = actions[b_index]
                b_returns = returns[b_index]
                b_old_logprobs = old_log_prob[b_index].detach()

                # critic_loss, actor_loss = self.train_batch(b_states, b_advants, b_actions, b_returns, b_old_logprobs)
                critic_loss, actor_loss = self.agent.train_batch(
                    b_states, b_advants, b_actions, b_returns, b_old_logprobs)
                
                self.train_count += 1
                self.writer.add_scalar('Actor loss', actor_loss.item(), self.train_count)
                self.writer.add_scalar('Critic loss', critic_loss.item(), self.train_count)

        return score_avg

    def test_episode(self, max_step=2048, save_gif=True):
        rb, rewards = self.agent.generate_epoch(
            self.test_env,
            epoch_size=1,
            max_episode_steps=max_step)
        self.test_count += 1
        self.writer.add_scalar(
            'Test reward', rewards[0][1], self.test_count)
        logging.info(f"Test  #{self.test_count:8d}: reward={rewards[0][1]:8.2f} steps={len(rb)}")
        if save_gif:
            frames = self.test_env.render()
            name = f'./run/{self.session_name}/{self.test_count}({rewards[0][1]:.2f}).gif'
            imageio.mimsave(name, frames, fps=30)

    def load(self, prefix: Literal['last', 'best']):
        self.agent.load(f"./run/{self.session_name}/{prefix}")
        with open(f"./run/{self.session_name}/{prefix}.run", 'r') as f:
            line = f.readline()
            ints = [int(x) for x in line.split(' ')]
            self.train_count = ints[0]
            self.test_count = ints[1]

    def save(self, prefix: Union[Literal['last', 'best'], str]):
        self.agent.save(f"./run/{self.session_name}/{prefix}")
        with open(f"./run/{self.session_name}/{prefix}.run", 'w') as f:
            f.write(f"{self.train_count} {self.test_count}")

    def run(self, total_train_steps=2000000, epoch_size=2048, batch_size=64, test_interval=40960):
        best_reward = -math.inf
        last_checkpoint = self.train_count // 100000
        while self.train_count < total_train_steps:
            if self.train_count // test_interval != (self.train_count-1) // test_interval:
                self.test_episode()
            rew = self.train_epoch(epoch_size=epoch_size, batch_size=batch_size)
            self.save('last')
            if rew > best_reward:
                best_reward = rew
                self.save('best')
            if self.train_count // 100000 > last_checkpoint:
                self.save(str(self.train_count // 100000))

    def test(self, count=10):
        for i in range(count):
            self.test_episode()
