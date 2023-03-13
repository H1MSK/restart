import onnx
from sys import argv

model = onnx.load(argv[1])

graph = model.graph

print(f"Inputs:")
for i, value in enumerate(graph.input):
    print(f"#{i}:\n{value}\n\n")
print(f"Outputs:")
for i, value in enumerate(graph.output):
    print(f"#{i}:\n{value}\n\n")
print("Nodes:")
for i, value in enumerate(graph.node):
    print(f"#{i}:\n{value}\n\n")
print("Values:")
for i, value in enumerate(graph.value_info):
    print(f"#{i}:\n{value}\n\n")
print("Initializers:")
for i, value in enumerate(graph.initializer):
    print(f"#{i}:")
    print("dims:", value.dims)
    print("data_type:", value.data_type)
    print("name:", value.name)