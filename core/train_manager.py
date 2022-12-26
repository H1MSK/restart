import math
import os
from typing import Literal, Optional, Union
import torch
from torch.utils.tensorboard.writer import SummaryWriter
import configparser
from param_choice import *
import imageio
import numpy as np
import logging
import core.config as config

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
            while os.path.exists(f'./run/{env_name}_{agent_name}_{model_name}_{iter}'):
                iter += 1
            session_name=f'{env_name}_{agent_name}_{model_name}_{iter}'
            os.mkdir(f'./run/{session_name}')
            self.conf = {"params": {}}
            self.conf["params"]["model"] = model_name
            self.conf["params"]["agent"] = agent_name
            self.conf["params"]["env"] = env_name
            self.conf["params"]["hidden_width"] = str(hidden_width)
            self.conf["params"]["seed"] = str(seed)
            self.conf["params"]["lr_actor"] = str(lr_actor)
            self.conf["params"]["lr_critic"] = str(lr_critic)
            config.save_config(f'./run/{session_name}/conf.ini', self.conf)
            need_load = False
        else:
            # No need to check existance since open(f, m) will raise errors
            self.conf = config.load_config(f'./run/{session_name}/conf.ini')
            need_load = True
            model_name = self.conf["params"]["model"]
            agent_name = self.conf["params"]["agent"]
            env_name = self.conf["params"]["env"]
            lr_actor = float(self.conf["params"]["lr_actor"])
            lr_critic = float(self.conf["params"]["lr_critic"])
            hidden_width = int(self.conf["params"]["hidden_width"])
            seed = int(self.conf["params"]["seed"])
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

    def test_episode(self, / , gif_name: str, max_step=2048, save_gif=True):
        assert(isinstance(gif_name, str))
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
            name = f'./run/{self.session_name}/{gif_name}.gif'
            imageio.mimsave(name, frames, fps=30)
            with open(f"./run/{self.session_name}/{gif_name}.result.txt", "wb") as f:
                f.write(f"{rewards[0]}".encode())

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

    def set_run(self, /, total_train_epochs=2000000, epoch_size=2048, max_episode_steps=10000, batch_size=64, test_interval=4096):
        self.conf.update({"run": {}})
        self.conf["run"].update({
            "steps": str(total_train_epochs),
            "epoch_size": str(epoch_size),
            "max_episode_step": str(max_episode_steps),
            "batch_size": str(batch_size),
            "test_interval": str(test_interval)
        })
        config.save_config(f'./run/{self.session_name}/conf.ini', self.conf)

    def run(self, total_train_epochs=2000000, epoch_size=2048, max_episode_steps=10000, batch_size=64, test_interval=4096):
        s = self.conf["run"]
        total_train_epochs = int(s["steps"])
        epoch_size = int(s["epoch_size"])
        max_episode_steps = int(s["max_episode_step"])
        batch_size = int(s["batch_size"])
        test_interval = int(s["test_interval"])

        logging.info(f"Running with total_train_epochs={total_train_epochs}, "
                     f"epoch_size={epoch_size}, "
                     f"max_episode_steps={max_episode_steps}, "
                     f"batch_size={batch_size}, "
                     f"test_interval={test_interval}"
        )

        best_reward = -math.inf
        while self.train_count < total_train_epochs:
            if self.train_count // test_interval != (self.train_count-1) // test_interval:
                self.test_episode(str(self.train_count // test_interval))
                self.save(str(self.train_count // test_interval))
            rew = self.train_epoch(epoch_size=epoch_size, batch_size=batch_size, max_episode_steps=max_episode_steps)
            self.save('last')
            if rew > best_reward:
                best_reward = rew
                self.save('best')

    def test(self, count=10):
        for i in range(count):
            self.test_episode(f"t{i}")
