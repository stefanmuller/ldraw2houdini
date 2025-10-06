import re
import json
import ldraw

resources = ldraw.resources()
ld_colors = resources / 'ld_colors.json'
brickini_colors = resources / 'brickini_colors.json'
ldconfig = ldraw.ldraw_lib() / 'LDConfig.ldr'

def read_ld_config():
    color_dict = {}
    # regular expressions for extracting information
    category_pattern = re.compile(r'0\s+//\s+LDraw\s+(.+)\s+Colours')
    color_pattern = re.compile(r'^0\s+!COLOUR\s+(\w+)\s+CODE\s+(\d+)\s+VALUE\s+([^\s]+)')

    current_category = ''
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
                # print (name)
                rgb = ldraw.hex_to_acescg(value)

                color_dict[code] = {
                    'category': current_category,
                    'name': name,
                    'rgb': rgb
                }
    return color_dict

def update_to_brickini_colors(color_dict):
    # load brickini_colors.json
    with open(brickini_colors, 'r') as f:
        ld_colors_dict = json.load(f)

    #update/overwrite original ldraw colors
    color_dict.update(ld_colors_dict)

    return color_dict

# The way this works is that I take the LDConfig.ldr that comes with lDraw
# and convert it to a more easily digestible json, alongside aces conversion.
# However, some colors aren't quite accurate (mostly transparent colors are way too dark)
# therefore I have a brickini_colors.json that I manually fill up with better colors.
# If a color exists in that file, it overwrites the one coming from LDraw.

color_dict = read_ld_config()
color_dict = update_to_brickini_colors(color_dict)

with open(ld_colors, 'w') as f:
    json.dump(color_dict, f, indent=4)
