import torch

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
