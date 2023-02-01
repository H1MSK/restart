part_name = "xc7z020-clg400-2"
synthesis_clock_period_ns = 1.0
implement_clock_period_MHz = 200

batch_size = 64

obs_size = 376
hidden_size = 64
act_size = 17
act_continuous = True


nn_in_size = obs_size
nn_out_size = act_size * 2 + 1
element_name = 'cm_float'
element_bitwidth = 32

nn_structures = (
    ("Fork", ),
        ("Linear", hidden_size, ),
        ("Tanh",),
        ("Linear", hidden_size, ),
        ("Tanh", ),
        ("Linear", 1, ),
    ("ForkAgain", ),
        ("Linear", hidden_size, ),
        ("Tanh", ),
        ("Linear", hidden_size, ),
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
