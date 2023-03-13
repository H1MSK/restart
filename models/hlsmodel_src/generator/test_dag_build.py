import dag
import os
import logging

logging.basicConfig(level=logging.DEBUG)

dag.build_from_structures(output_debug_pngs=True)

print(os.path.abspath(os.curdir))
print("done")
dag.output_dag("generated_dag.png")
print(dag.report_cache_usage())
print(dag.report_param_usage())
