part_name = "xc7z020-clg400-2"
synthesis_clock_period_ns = 1.0
implement_clock_period_MHz = 166.666666

batch_size = 64

obs_size = 27
act_size = 8
act_continuous = True


nn_in_size = min(obs_size, 376)
nn_hidden_size = 64
nn_out_size = act_size * 2 + 1
element_name = 'cm_float'
element_bitwidth = 32

assert(nn_in_size <= obs_size)
enable_pca = (nn_in_size < obs_size)

nn_structures = (
    ("Fork", ),
        ("Linear", nn_hidden_size, ),
        ("Tanh",),
        ("Linear", nn_hidden_size, ),
        ("Tanh", ),
        ("Linear", 1, ),
    ("ForkAgain", ),
        ("Linear", nn_hidden_size, ),
        ("Tanh", ),
        ("Linear", nn_hidden_size, ),
        ("Tanh", ),
        ("Fork", ),
            ("Linear", act_size, ),
        ("ForkAgain", ),
            ("Linear", act_size, ),
            ("Exp", ),
        ("Cat", ),
    ("Cat", )
)

def _validate():
    for i in nn_structures:
        assert(isinstance(i, tuple) and isinstance(i[0], str))
_validate()
