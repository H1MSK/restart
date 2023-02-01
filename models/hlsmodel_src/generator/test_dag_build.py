import dag
from params import nn_structures
import os
import logging

logging.basicConfig(level=logging.DEBUG)

dag.build()

print(os.path.abspath(os.curdir))
print("done")
dag.net.output_dag("generated_dag.png")
print(dag.net.report_cache_usage())
print(dag.net.report_param_usage())
