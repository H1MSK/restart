import torch
import numpy as np

def gae(length, rewards, masks, pred_values, discount, lambda_gae):
    returns = torch.zeros(size=(length, 1), dtype=torch.float32)
    advants = torch.zeros(size=(length, 1), dtype=torch.float32)
    running_returns = 0
    previous_value = 0
    running_advants = 0

    for t in reversed(range(0, len(rewards))):
        running_returns = rewards[t] + \
            discount * running_returns * masks[t]
        running_tderror = rewards[t] + discount * \
            previous_value * masks[t] - pred_values[t]
        running_advants = running_tderror + discount * \
            lambda_gae * running_advants * masks[t]

        previous_value = pred_values[t]
        if t < length:
            returns[t] = running_returns
            advants[t] = running_advants
    # returns = (returns - returns.mean()) / returns.std()
    advants = (advants - advants.mean()) / advants.std()
    return returns, advants


class RolloutBuffer():
    def __init__(self,
                 discount=0.98,
                 lambda_gae=0.98) -> None:
        self.obs = []
        self.acts = []
        self.rewards = []
        self.pred_values = []
        self.target_logprobs = []
        self.masks = []
        self.n = 0
        self.finished = False
        self.discount = discount
        self.lambda_gae = lambda_gae

    def append(self,
               obs: torch.Tensor,
               act: torch.Tensor,
               reward: float,
               pred_value: float,
               target_logprob, terminated):
        assert (not self.finished)
        self.obs.append(obs)
        self.acts.append(act)
        self.rewards.append(reward)
        self.pred_values.append(pred_value)
        self.target_logprobs.append(target_logprob)
        self.masks.append((1 - terminated) * 1)
        self.n += 1

    def convert_to_gae(self):
        returns, advants = gae(
                len(self.obs),
                self.rewards,
                self.masks,
                self.pred_values,
                self.discount,
                self.lambda_gae)
        self.returns = returns
        self.advants = advants
        self.obs = torch.vstack(self.obs)
        self.acts = torch.vstack(self.acts)
        self.target_logprobs = torch.tensor(self.target_logprobs, dtype=torch.float32).unsqueeze(1)

        self.rewards = None
        self.masks = None
        # self.pred_values = None
        self.finished = True