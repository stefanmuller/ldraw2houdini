from pathlib import Path
import json
import hou

def ldraw_lib():
    partlib = Path(hou.getenv('LDRAW_LIB'))
    return partlib

def color_lib():
    this_file = Path(__file__).resolve()
    color_config = this_file.parent.parent / 'resources' / 'ld_colors.json'

    with open(color_config, 'r') as f:
        color_dict = json.load(f)
    return color_dict