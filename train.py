import logging
from sys import argv
from train_args import parse
from core.train_manager import TrainManager

if __name__ == '__main__':
    args = parse(argv=argv[1:])

    total_train_epochs=args.total_train_epochs
    max_episode_step=args.max_episode_step
    min_epoch_size=args.min_epoch_size
    batch_size=args.batch_size

    logging.basicConfig(level=logging.INFO)
    logging.info(f"Args={args}")
    if args.session != None:
        tm = TrainManager(session_name=args.session)
    else:
        tm = TrainManager(
            model_name=args.model,
            agent_name=args.agent,
            env_name=args.env,
            lr_actor=args.lr_actor,
            lr_critic=args.lr_critic,
            hidden_width=args.hidden_width,
            seed=args.seed,
            use_orthogonal_init=args.orthogonal_init
        )
        tm.set_run(
            total_train_epochs=total_train_epochs,
            max_episode_steps=max_episode_step,
            epoch_size=min_epoch_size,
            batch_size=batch_size)
    
    tm.run()
