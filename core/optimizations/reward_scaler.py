import torch
from .running_mean_std import RunningMeanStd

class RewardScaler:
    def __init__(self, shape, gamma, device):
        self.shape = shape  # reward shape=1
        self.gamma = gamma  # discount factor
        self.device = torch.device(device)
        self.running_ms = RunningMeanStd(shape=self.shape)
        self.R = torch.zeros(self.shape, device=self.device)

    def __call__(self, x):
        self.R = self.gamma * self.R + x
        self.running_ms.update(self.R)
        x = x / (self.running_ms.std + 1e-8)  # Only divided std
        return x

    def reset(self):  # When an episode is done,we should reset 'self.R'
        self.R = torch.zeros(self.shape, device=self.device)
