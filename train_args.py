import argparse
from param_choice import *

def parse(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--session', type=str, help='Continue session name')

    parser.add_argument('--lr_actor', type=float, default=3e-4, help='Learning rate for actor')
    parser.add_argument('--lr_critic', type=float, default=3e-4, help='Learning rate for critic')
    parser.add_argument('--hidden_width', type=int, default=64, help='Width of hidden layers')

    parser.add_argument('--seed', type=int, default=0, help='Environment seed')

    default_model=None
    for i in model_choices.keys():
        default_model=i
        break

    default_agent=None
    for i in agent_choices.keys():
        default_agent=i
        break

    default_env=None
    for i in env_choices.keys():
        default_env=i
        break

    parser.add_argument('-m', '--model', choices=model_choices.keys(),
                     default=default_model, help='Model type')
    parser.add_argument('-a', '--agent', choices=agent_choices.keys(),
                     default=default_agent, help='Agent type')
    parser.add_argument('-e', '--env', choices=env_choices.keys(),
                     default=default_env, help='Environment name')
    args = parser.parse_args(argv)
    return args
