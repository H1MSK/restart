import logging
import re
from typing import Dict

log = logging.getLogger("Config")

_validator=re.compile(r"[\[\]=\\]")
_section_name = re.compile(r"^\[(.+)\]$")
_value_pair = re.compile(r"^([^=\[\]\n]+?)\W*=\W*([^=\[\]\n]+?)\W*$")

def _genlines(name:str, d:dict):
    assert(0 == len(_validator.findall(name)))
    lines=[f"[{name}]\n"]
    for k, v in d.items():
        assert(isinstance(k, str) and isinstance(v, str))
        assert(0 == len(_validator.findall(k + v)))
        lines.append(f"{k} = {v}\n")
    return lines

def save_config(file: str, d: dict):
    with open(file, "w") as f:
        for key, value in d.items():
            f.writelines(_genlines(key, value))

def load_config(file):
    a:Dict[str, Dict[str, str]] = {}
    with open(file, "r") as f:
        current_section = None
        current_dict: Dict[str, str] = {}
        for line in f:
            line = line[:-1]
            sect = _section_name.match(line)
            if sect != None:
                if current_section != None and len(current_dict) > 0:
                    a.update({current_section: current_dict})
                current_section = sect.group(1)
                current_dict = {}
                continue
            pair = _value_pair.match(line)
            if pair != None:
                current_dict[pair.group(1)] = pair.group(2)
        
    if current_section != None and len(current_dict) > 0:
        a.update({current_section: current_dict})
    return a
