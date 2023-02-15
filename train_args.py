import argparse
from param_choice import *

def parse(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--session', type=str, help='Continue session name')

    parser.add_argument('--lr_actor', type=float, default=3e-4, help='Learning rate for actor')
    parser.add_argument('--lr_critic', type=float, default=3e-4, help='Learning rate for critic')
    parser.add_argument('--hidden_width', type=int, default=64, help='Width of hidden layers')

    parser.add_argument('--seed', type=int, default=0, help='Environment seed')

    parser.add_argument('--total_train_epochs', type=int, default=2000000, help='Total count of trained epochs')
    parser.add_argument('--max_episode_steps', type=int, default=10000, help='Max steps in each episode')
    parser.add_argument('--min_epoch_size', type=int, default=2048, help='Minimum steps in each epoch')
    parser.add_argument('--batch_size', type=int, default=64, help='Batch size')
    parser.add_argument('--test_interval', type=int, default=4096, help='Test once after trainning this many episodes')

    parser.add_argument('--orthogonal_init', action='store_true', help='Use orthogonal initialization for linear layers')

    parser.add_argument('--pca_dim', type=int, default=0, help='PCA output dimensionality, 0 for disable')

    parser.add_argument('--store_obs', action='store_true', help='Store observations to obs.sav.[num].npz')

    parser.add_argument('--obs_cut_start', type=int, default=0, help='Observation cut range start, inclusive')
    parser.add_argument('--obs_cut_end', type=int, default=-1, help='Observation cut range end, exclusive')


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
