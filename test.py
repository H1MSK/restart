import logging
from sys import argv
from train_args import parse
from core.train_manager import TrainManager

if __name__ == '__main__':
    args = parse(argv=argv[1:])
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Args={args}")
    if args.session != None:
        tm = TrainManager(session_name=args.session)
    else:
        raise ValueError("Session should be indicated for test.")
        # tm = TrainManager(
        #     model_name=args.model,
        #     agent_name=args.agent,
        #     env_name=args.env,
        #     lr_actor=args.lr_actor,
        #     lr_critic=args.lr_critic,
        #     hidden_width=args.hidden_width,
        #     seed=args.seed
        # )
    tm.test()
