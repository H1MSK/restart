import sys 
sys.path.append(".")

from models.pymodel import PyActorCritic
import torch
import torch.onnx
import onnxoptimizer
import os

obs_size = 27
act_size = 8

pyac = PyActorCritic(obs_size, act_size)

x = torch.randn((1, 27), requires_grad=True)

o = pyac.forward(x)

output_filename = f"generated.{pyac.obs_dim}.{pyac.act_dim}.{pyac.hidden_width}.onnx"

torch.onnx.export(pyac.model,
                  x,
                  output_filename,
                  input_names=['input'],
                  output_names=['value', 'mu', 'sigma'],
                  dynamic_axes={'input' : {0 : 'batch_size'},
                                'value' : {0 : 'batch_size'},
                                'mu' : {0 : 'batch_size'},
                                'sigma' : {0 : 'batch_size'}})

# os.system(f"python -m onnxoptimizer {output_filename} {output_filename}")
# os.system(f"python -m onnxsim {output_filename} {output_filename}")
