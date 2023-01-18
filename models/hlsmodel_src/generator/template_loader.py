import os
import string

def load_template(*names):
    with open(os.path.join(
        os.path.dirname(__file__),
        "templates",
        *names
    )) as f:
        content = f.read()

    t = string.Template(content)
    return t