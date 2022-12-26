try:
    import gym
except ImportError:
    import gymnasium as gym

from models.cmodel import CActirCritic
from models.pymodel import PyActorCritic
from core.agent import PPOAgent

model_choices = {
    'py': PyActorCritic,
    'c': CActirCritic
}

agent_choices = {
    'ppo': PPOAgent
}

env_choices = {
    'LunarLanderContinuous': (lambda **kwargs: gym.make('LunarLanderContinuous-v2', **kwargs)),
    'Humanoid': (lambda **kwargs: gym.make('Humanoid-v4', healthy_reward=3.0, **kwargs)),
    'Walker2D': (lambda **kwargs: gym.make('Walker2d-v4', **kwargs)),
    'HalfCheetah': (lambda **kwargs: gym.make('HalfCheetah-v4', **kwargs)),
}
