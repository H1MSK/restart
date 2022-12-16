
## 0 - Train Manager

- Tensorboard log
- Session manage: parameters save and load
- Train / test function

## 1 - Agent

- Give actions based on network outputs
- Gradient calculate of network outputs (PPO, DPPS, LDPPS)
- Generate rollout buffers
- Observation normalize
- Reward scaling
- LR Decay
- ... Other optimizations

## 2 - *ActorCritic

- Wrap model and give generalized API to upper layers
- Export LR and other hyper parameters
- Optimize model

## 3 - *Model

Handles:
- Parameter save/load
- Network forward
- Network backward based on grad of output
