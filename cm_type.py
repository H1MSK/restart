import numpy as np
import torch
from ctypes import c_float, POINTER

cm_float = c_float
torch_cm_float = torch.float32
np_cm_float = np.float32
cm_float_p = POINTER(cm_float)

def get_float_pointer(tensor: torch.Tensor):
    arr = tensor.numpy()
    assert(arr.data.contiguous and arr.dtype == np_cm_float)
    return arr.ctypes.data
