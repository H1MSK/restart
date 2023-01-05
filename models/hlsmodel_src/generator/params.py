part_name = "xc7z020-clg400-2"
clock_period = "500MHz"


obs_size = 376
hidden_size = 64
act_size = 17
act_continuous = True


nn_structures = (
    ("Fork", ),
        ("Linear", obs_size, hidden_size),
        ("Tanh", hidden_size),
        ("Linear", hidden_size, hidden_size),
        ("Tanh", hidden_size),
        ("Linear", hidden_size, 1),
    ("ForkAgain", ),
        ("Linear", obs_size, hidden_size),
        ("Tanh", hidden_size),
        ("Linear", hidden_size, hidden_size),
        ("Tanh", hidden_size),
        ("Fork", ),
            ("Linear", hidden_size, act_size),
        ("ForkAgain", ),
            ("Linear", hidden_size, act_size),
            ("Exp", act_size),
        ("ForkEnd", ),
    ("ForkEnd", )
)
