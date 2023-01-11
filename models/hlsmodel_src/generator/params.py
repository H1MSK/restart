part_name = "xc7z020-clg400-2"
clock_period = "500MHz"


obs_size = 376
hidden_size = 64
act_size = 17
act_continuous = True


nn_in_size = obs_size
nn_out_size = act_size * 2 + 1
element_name = 'cm_float'
element_bitwidth = 32

nn_structures = (
    ("Fork", obs_size),
        ("Linear", obs_size, hidden_size),
        ("Tanh", hidden_size),
        ("Linear", hidden_size, hidden_size),
        ("Tanh", hidden_size),
        ("Linear", hidden_size, 1),
    ("ForkAgain", obs_size),
        ("Linear", obs_size, hidden_size),
        ("Tanh", hidden_size),
        ("Linear", hidden_size, hidden_size),
        ("Tanh", hidden_size),
        ("Fork", hidden_size),
            ("Linear", hidden_size, act_size),
        ("ForkAgain", hidden_size),
            ("Linear", hidden_size, act_size),
            ("Exp", act_size),
        ("Cat", act_size * 2),
    ("Cat", act_size * 2 + 1)
)
