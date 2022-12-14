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

    
    def _train_epoch0(self, seed=None, epoch_size=2048, max_overrun=0, epoch=1, batch_size=64):
        episodes = 0
        eva_episodes = 0
        
        memory = []
        scores = []
        steps = 0
        print(f"Sync state1:{torch.rand(1)} {np.random.rand()}")
        while steps <2048: #Horizen
            episodes += 1
            s = self.agent.obs_normalizer(self.train_env.reset()[0])
            score = 0
            for _ in range(epoch_size):
                steps += 1
                #选择行为
                a = self.agent.choose_action(torch.from_numpy(np.array(s).astype(np.float32)).unsqueeze(0))[0]

                s_ , r ,done, _,info = self.train_env.step(a)
                s_ = self.agent.obs_normalizer(s_)

                mask = (1-done)*1
                memory.append([s,a,r,mask])

                score += r
                s = s_
                if done:
                    break
                
            scores.append((steps, score))

        for step, score in scores:
            self.writer.add_scalar("Episode reward", score, batch_size * self.train_count + step)
        score_avg = sum(i[1] for i in scores) / len(scores)

        memory = np.array(memory)
        states = torch.tensor(np.vstack(memory[:,0]),dtype=torch.float32)

        actions = torch.tensor(list(memory[:,1]),dtype=torch.float32)
        rewards = torch.tensor(list(memory[:,2]),dtype=torch.float32)
        masks = torch.tensor(list(memory[:,3]),dtype=torch.float32)

        values = self.agent.ac.model.critic_net(states).detach()

        returns,advants = gae(len(memory), rewards, masks, values, 0.98, 0.98)
        old_f = self.agent.ac.model.act_feat_net(states)
        old_mu = self.agent.ac.model.mu_net(old_f)
        old_rho = self.agent.ac.model.rho_net(old_f)
        old_std = torch.exp(old_rho)
        pi = self.agent.distribution(old_mu,old_std)

        old_log_prob = pi.log_prob(actions).sum(1,keepdim=True)

        n = len(states)
        arr = np.arange(n)
        for epoch in range(1):
            np.random.shuffle(arr)
            for i in range(n//batch_size):
                b_index = arr[batch_size*i:batch_size*(i+1)]
                b_states = states[b_index]
                b_advants = advants[b_index]
                b_actions = actions[b_index]
                b_returns = returns[b_index]

                mu, std = self.agent.ac.act(b_states)

                pi = self.agent.distribution(mu,std)
                new_prob = pi.log_prob(b_actions).sum(1,keepdim=True)
                old_prob = old_log_prob[b_index].detach()
                #KL散度正则项
               # KL_penalty = self.kl_divergence(old_mu[b_index],old_std[b_index],mu,std)
                ratio = torch.exp(new_prob-old_prob)

                surrogate_loss = ratio*b_advants
                values = self.agent.ac.model.critic_net(b_states)

                critic_loss = self.agent.critic_loss_func(values,b_returns)

                self.agent.ac.optim_critic.zero_grad()
                critic_loss.backward()
                self.agent.ac.optim_critic.step()

                ratio = torch.clamp(ratio,1.0-self.agent.epsilon,1.0+self.agent.epsilon)

                clipped_loss =ratio*b_advants

                actor_loss = -torch.min(surrogate_loss,clipped_loss).mean()
                #actor_loss = -(surrogate_loss-beta*KL_penalty).mean()

                self.agent.ac.optim_actor.zero_grad()
                actor_loss.backward()

                self.agent.ac.optim_actor.step()

                print(f"Sync state3: {actor_loss} {critic_loss}")

                self.train_count += 1
                self.writer.add_scalar('Actor loss', actor_loss.item(), self.train_count)
                self.writer.add_scalar('Critic loss', critic_loss.item(), self.train_count)

        return score_avg

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

    def _calculate_gae(self, memory, states):
        rewards = torch.tensor(list(memory[:,2]),dtype=torch.float32)
        masks = torch.tensor(list(memory[:,3]),dtype=torch.float32)

        values = self.agent.ac.model.critic_net(states).detach()

        returns,advants = gae(len(memory), rewards, masks, values, 0.98, 0.98)
        return returns,advants

    def _train_batch(self, b_states, b_advants, b_actions, b_returns, old_prob):
        mu, std = self.agent.ac.act(b_states)

        pi = self.agent.distribution(mu,std)
        new_prob = pi.log_prob(b_actions).sum(1,keepdim=True)
                #KL散度正则项
               # KL_penalty = self.kl_divergence(old_mu[b_index],old_std[b_index],mu,std)
        ratio = torch.exp(new_prob-old_prob)

        surrogate_loss = ratio*b_advants
        # values = self.agent.ac.model.critic_net(b_states)
        values = self.agent.ac.critic(b_states)

        critic_loss = self.agent.critic_loss_func(values,b_returns)

        # self.agent.ac.optim_critic.zero_grad()
        self.agent.ac.critic_zero_grad()
        critic_loss.backward()
        # self.agent.ac.optim_critic.step()
        self.agent.ac.critic_step()

        ratio = torch.clamp(ratio,1.0-self.agent.epsilon,1.0+self.agent.epsilon)

        clipped_loss =ratio*b_advants

        actor_loss = -torch.min(surrogate_loss,clipped_loss).mean()
                #actor_loss = -(surrogate_loss-beta*KL_penalty).mean()

        # self.agent.ac.optim_actor.zero_grad()
        self.agent.ac.actor_zero_grad()
        actor_loss.backward()
        # self.agent.ac.optim_actor.step()
        self.agent.ac.actor_step()
        
        return critic_loss, actor_loss

    def _generate_epoch(self, epoch_size, max_episode_steps):
        episodes = 0
        eva_episodes = 0
        
        memory = []
        scores = []
        steps = 0
        print(f"Sync state1:{torch.rand(1)} {np.random.rand()}")
        while steps < epoch_size: #Horizen
            episodes += 1
            s = self.agent.obs_normalizer(self.train_env.reset()[0])
            score = 0
            for _ in range(max_episode_steps):
                steps += 1
                #选择行为
                a = self.agent.choose_action(torch.from_numpy(np.array(s).astype(np.float32)).unsqueeze(0))[0]

                s_ , r ,done, _,info = self.train_env.step(a)
                s_ = self.agent.obs_normalizer(s_)

                mask = (1-done)*1
                memory.append([s,a,r,mask])

                score += r
                s = s_
                if done:
                    break
                
            scores.append((steps, score))
        return memory,scores

    def _train_epoch1(self, seed=None, epoch_size=2048, max_episode_steps=10000, epoch=1, batch_size=64):

        # generate method 1 {
        # episodes = 0
        # rewards: List[Tuple[int, float]] = []
        # steps = 0
        # rb = RolloutBuffer(
        #     self.agent.obs_dim,
        #     self.agent.act_dim,
        #     max_len=2048,
        #     max_overrun=2048
        # )
        # while steps < 2048: #Horizen
        #     episodes += 1
        #     s = self.agent.obs_normalizer(self.train_env.reset()[0])
        #     score = 0
        #     for _ in range(2048):
        #         steps += 1
        #         #选择行为
        #         o = torch.from_numpy(np.array(s).astype(np.float32)).unsqueeze(0)
        #         f = self.agent.ac.model.act_feat_net(o)
        #         mu = self.agent.ac.model.mu_net(f)
        #         rho = self.agent.ac.model.rho_net(f)
        #         sigma = torch.exp(rho)
        #         dist = self.agent.distribution(mu, sigma)
        #         a = dist.sample()[0]
        #         s_ , r ,done, _,info = self.train_env.step(a)
        #         s_ = self.agent.obs_normalizer(s_)

        #         rb.append(torch.tensor(s), a, r, 0, 0, done)

        #         score += r
        #         s = s_
        #         if done:
        #             break
        #     rewards.append((steps, score))
        
        # } end generate method 1

        # generate method 2 {
        rb, rewards = self.agent.generate_rb(
            self.train_env,
            stop_when_terminated=False,
            max_steps=epoch_size,
            max_episode_steps=max_episode_steps,
            training=True)

        # rb.convert_to_gae()
        # } end generate method 2


        for i, r in rewards:
            self.writer.add_scalar('Train reward', r, self.train_count * batch_size + i)

        average_reward = sum(x[1] for x in rewards) / len(rewards)


        # Run method 1 {

        # rb.convert_to_gae()
        
        # states = rb.obs
        # actions = rb.acts
        # old_log_prob = rb.target_logprobs
        # advants = rb.advants
        # returns = rb.returns
        # # rewards = rb.rewards
        # # masks = rb.masks

        # # values = self.agent.ac.model.critic_net(states)

        # # returns, advants = gae(epoch_size, rewards, masks, values, 0.98, 0.98)


        # # old_feat = self.agent.ac.model.act_feat_net(states)
        # # old_mu = self.agent.ac.model.mu_net(old_feat)
        # # old_rho = self.agent.ac.model.rho_net(old_feat)
        # # old_sigma = torch.exp(old_rho)
        # # pi = self.agent.distribution(old_mu, old_sigma)

        # # old_log_prob = pi.log_prob(actions).sum(1, keepdim=True)

        # cl = []
        # al = []
        # el = []

        # for ep in range(epoch):
        #     randperm = torch.randperm(epoch_size)
        #     for i in range(0, epoch_size, batch_size):
        #         b_index = randperm[i:i+batch_size]
        #         b_states = states[b_index]
        #         b_advants = advants[b_index]
        #         b_actions = actions[b_index]
        #         b_returns = returns[b_index]

        #         feat = self.agent.ac.model.act_feat_net(b_states)
        #         mu = self.agent.ac.model.mu_net(feat)
        #         rho = self.agent.ac.model.rho_net(feat)
        #         sigma = torch.exp(rho)
        #         pi = self.agent.distribution(mu, sigma)
        #         new_prob = pi.log_prob(b_actions).sum(1, keepdim=True)
        #         old_prob = old_log_prob[b_index].detach()

        #         ratio = torch.exp(new_prob - old_prob)

        #         surrogate_loss = ratio*b_advants
        #         values = self.agent.ac.model.critic_net(b_states)

        #         critic_loss = self.agent.critic_loss_func(values,b_returns)

        #         self.agent.ac.optim_critic.zero_grad()
        #         critic_loss.backward()
        #         self.agent.ac.optim_critic.step()

        #         ratio = torch.clamp(ratio,1.0-self.agent.epsilon,1.0+self.agent.epsilon)

        #         clipped_loss =ratio*b_advants

        #         actor_loss = -torch.min(surrogate_loss,clipped_loss).mean()
        #         #actor_loss = -(surrogate_loss-beta*KL_penalty).mean()

        #         self.agent.ac.optim_actor.zero_grad()
        #         actor_loss.backward()

        #         self.agent.ac.optim_actor.step()

        #         self.train_count += 1
        #         self.writer.add_scalar(
        #             'Critic loss', critic_loss, self.train_count)
        #         self.writer.add_scalar(
        #             'Actor loss', actor_loss, self.train_count)
        #         # self.writer.add_scalar(
        #         #     'Entropy loss', entropy_loss, self.train_count)

        #         cl.append(critic_loss.item())
        #         al.append(actor_loss.item())
        #         el.append(0)


        # logging.info(f"Train #{self.train_count:8d}: reward={average_reward:8.2f} "
        #              f"loss={sum(cl)/len(cl):10.4f}/{sum(al)/len(al):10.4f}/{sum(el)/len(el):10.4f}")

        # return average_reward

        # } End run method 1

        # Run method 2 {
        rb.convert_to_gae()
        cl = []
        al = []
        el = []

        for ep in range(epoch):
            randperm = torch.randperm(epoch_size)
            for i in range(0, epoch_size, batch_size):
                idx = randperm[i:i+batch_size]
                b_obs = rb.obs[idx, :]
                b_acts = rb.acts[idx, :]
                b_target_logprobs = rb.target_logprobs[idx, :]
                b_returns = rb.returns[idx, :]
                b_advantages = rb.advants[idx, :]
                critic_loss, actor_loss, entropy_loss = self.agent.train_batch(
                    b_obs=b_obs,
                    b_acts=b_acts,
                    b_target_logprobs=b_target_logprobs,
                    b_returns=b_returns,
                    b_advantages=b_advantages)
                cl.append(critic_loss)
                al.append(actor_loss)
                el.append(entropy_loss)

                self.train_count += batch_size
                self.writer.add_scalar(
                    'Critic loss', critic_loss, self.train_count)
                self.writer.add_scalar(
                    'Actor loss', actor_loss, self.train_count)
                self.writer.add_scalar(
                    'Entropy loss', entropy_loss, self.train_count)

        average_reward = sum(x[1] for x in rewards) / len(rewards)

        logging.info(f"Train #{self.train_count:8d}: reward={average_reward:8.2f} "
                     f"loss={sum(cl)/len(cl):10.4f}/{sum(al)/len(al):10.4f}/{sum(el)/len(el):10.4f}")

        return average_reward

        # } End run method 2

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
