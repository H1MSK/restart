from typing import Literal


part_name = "xc7z020-clg400-2"
synthesis_clock_period_ns = 8
synthesis_clock_uncertainty = "10%"
implement_clock_period_MHz = 125

batch_size = 64

obs_size = 27
act_size = 8
act_continuous = True


nn_in_size = min(obs_size, 376)
nn_hidden_size = 64
nn_out_size = act_size * 2 + 1
element_name = 'cm_float'
element_bitwidth = 32

enable_pca = (nn_in_size < obs_size)

use_cache_debug_bridge: Literal[1, 0]=0
cache_on_bridge_module: Literal['cache_reader', 'cache_loader'] = 'cache_loader'
cache_off_bridge_module: Literal['cache_writter', 'cache_extractor'] = 'cache_extractor'

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
    assert(nn_in_size <= obs_size)
    assert(use_cache_debug_bridge in (0, 1))
    assert(cache_on_bridge_module in ('cache_reader', 'cache_loader'))
    assert(cache_off_bridge_module in ('cache_writter', 'cache_extractor'))
_validate()
