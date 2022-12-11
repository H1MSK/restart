
## Top - Train Manager

Handles:
- LR Decay
- Tensorboard log

## 1 - Agent

Handles:
- Giving actions based on network outputs
- Observation normalize
- Generate rollout buffers
- Minibatch gradient calculate

## 1 - RolloutBuffer

Handles:
- Trajectory store
- GAE

## 2 - *ActorCritic

Exports:
- LR

Handles:
- Optimizer zero grad
- Optimizer step

## 3 - *Model

Handles:
- Network forward
- Network backward
