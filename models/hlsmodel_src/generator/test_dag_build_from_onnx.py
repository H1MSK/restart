import dag
import os
import logging
from sys import argv

logging.basicConfig(level=logging.DEBUG)

dag.build_from_onnx_file(argv[1], output_debug_pngs=True)

print(os.path.abspath(os.curdir))
print("done")
dag.output_dag("generated_dag.png")
print(dag.report_cache_usage())
print(dag.report_param_usage())
