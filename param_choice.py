import gym
from models.pymodel import PyActorCritic
from py.agent import PPOAgent

model_choices = {
    'py': PyActorCritic
}

agent_choices = {
    'ppo': PPOAgent
}

env_choices = {
    'LunarLanderContinuous': (lambda **kwargs: gym.make('LunarLanderContinuous-v2', **kwargs)),
    'Humanoid': (lambda **kwargs: gym.make('Humanoid-v4', healthy_reward=3.0, **kwargs))
}
