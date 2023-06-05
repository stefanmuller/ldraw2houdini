from pathlib import Path, PureWindowsPath
import re
import json


resources = Path(__file__).resolve().parent.parent / 'resources' / 'ld_colors.json'
ldconfig = '/home/stefan/ldraw/LDConfig.ldr'

def hex_to_rgb(hex_value):
    # Convert hex to decimal RGB values
    decimal_r = int(hex_value[0:2], 16)
    decimal_g = int(hex_value[2:4], 16)
    decimal_b = int(hex_value[4:6], 16)

    # Convert decimal RGB to linear sRGB
    linear_r = (decimal_r / 255) ** 2.2
    linear_g = (decimal_g / 255) ** 2.2
    linear_b = (decimal_b / 255) ** 2.2

    # Return as list
    return [linear_r, linear_g, linear_b]

color_dict = {}

# regular expressions for extracting information
category_pattern = re.compile(r'0\s+//\s+LDraw\s+(.+)\s+Colours')
color_pattern = re.compile(r'^0\s+!COLOUR\s+(\w+)\s+CODE\s+(\d+)\s+VALUE\s+([^\s]+)')

with open(ldconfig, 'r') as f:
    for line in f:

        # check if the line contains the category information
        category_match = category_pattern.match(line)
        if category_match:
            current_category = category_match.group(1)

        # check if the line contains color information
        match = color_pattern.match(line)
        if match:
            name, code, value = match.groups()
            value= value.replace('#','')
            print (name)
            rgb = hex_to_rgb(value)

            color_dict[code] = {
                'category': current_category,
                'name': name,
                'rgb': rgb
            }


with open(resources, 'w') as f:
    json.dump(color_dict, f, indent=4)

