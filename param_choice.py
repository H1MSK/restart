try:
    import gym
except ImportError:
    import gymnasium as gym

from models.cmodel import CActirCritic
from models.hls_simmodel import HlsSimActorCritic
from models.pymodel import PyActorCritic
from models.light_pymodel import LPyActorCritic
from models.hlsmodel import HlsActorCritic
from core.agent import DPPSAgent, PPOAgent

model_choices = {
    'py': PyActorCritic,
    'c': CActirCritic,
    'lpy': LPyActorCritic,
    'hlssim': HlsSimActorCritic,
    'hls': HlsActorCritic
}

agent_choices = {
    'ppo': PPOAgent,
    'dpps': DPPSAgent
}

env_choices = {
    'LunarLanderContinuous': 'LunarLanderContinuous-v2',
    'Humanoid': 'Humanoid-v4',
    'Walker2D': 'Walker2d-v4',
    'HalfCheetah': 'HalfCheetah-v4',
    'Ant': 'Ant-v4',
}
