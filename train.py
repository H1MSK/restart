import logging
from sys import argv
from train_args import parse
from core.train_manager import TrainManager

if __name__ == '__main__':
    args = parse(argv=argv[1:])

    total_train_epochs=args.total_train_epochs
    total_train_steps=args.total_train_steps
    max_episode_step=args.max_episode_steps
    min_epoch_size=args.min_epoch_size
    batch_size=args.batch_size
    test_interval=args.test_interval
    pca_dim=args.pca_dim
    store_obs=args.store_obs
    obs_cut_start=args.obs_cut_start
    obs_cut_end=args.obs_cut_end
    epoch=args.epoch
    discount=args.discount
    lambda_gae=args.lambda_gae

    if total_train_epochs == 0 and total_train_steps == 0:
        raise ValueError("Either total_train_epochs or total_train_steps should be set")
    elif total_train_epochs != 0 and total_train_steps != 0:
        logging.info("Both total_train_epochs and total_train_steps are set. OR condition is applied.")

    parameter_decay = args.parameter_decay

    logging.basicConfig(level=logging.INFO)
    logging.info(f"Args={args}")
    if args.session != None:
        tm = TrainManager(session_name=args.session)
    else:
        tm = TrainManager(
            model_name=args.model,
            agent_name=args.agent,
            env_name=args.env,
            num_envs=args.envs,
            lr_actor=args.lr_actor,
            lr_critic=args.lr_critic,
            hidden_width=args.hidden_width,
            seed=args.seed,
            enable_test=(test_interval > 0),
            use_orthogonal_init=args.orthogonal_init,
            pca_dim=pca_dim,
            obs_cut_start=obs_cut_start,
            obs_cut_end=obs_cut_end,
            store_obs=store_obs
        )
        tm.set_run(
            total_train_epochs=total_train_epochs,
            total_train_steps=total_train_steps,
            max_episode_steps=max_episode_step,
            epoch_size=min_epoch_size,
            epoch=epoch,
            batch_size=batch_size,
            test_interval=test_interval,
            discount=discount,
            lambda_gae=lambda_gae,
            parameter_decay=parameter_decay)
    
    tm.run()
