from pathlib import Path
import re
import json

resources = Path(__file__).resolve().parent.parent / 'resources' 
ld_colors = resources / 'ld_colors.json'
brickini_colors = resources / 'brickini_colors.json'
ldconfig = '/home/stefan/ldraw/LDConfig.ldr'

def hex_to_acescg(hex_value):
    # Convert hex to float rgb
    r = int(hex_value[0:2], 16) / 255
    g = int(hex_value[2:4], 16) / 255
    b = int(hex_value[4:6], 16) / 255

    # convert srgb to linear
    r = (r / 12.92) if r <= 0.04045 else ((r + 0.055) / 1.055) ** 2.4
    g = (g / 12.92) if g <= 0.04045 else ((g + 0.055) / 1.055) ** 2.4
    b = (b / 12.92) if b <= 0.04045 else ((b + 0.055) / 1.055) ** 2.4

    # thanks to Michael on acescentral.com
    # Generated using the Bradford CAT on https://www.colour-science.org:8010/apps/rgb_colourspace_transformation_matrix
    m = [[0.613132422390542, 0.339538015799666, 0.047416696048269],
        [0.070124380833917, 0.916394011313573, 0.013451523958235],
        [0.020587657528185, 0.109574571610682, 0.869785404035327]]

    #convert linear rgb to acescg
    acescg = [m[0][0] * r + m[0][1] * g + m[0][2] * b,
            m[1][0] * r + m[1][1] * g + m[1][2] * b,
            m[2][0] * r + m[2][1] * g + m[2][2] * b]

    return acescg

def read_ld_config():
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
                # print (name)
                rgb = hex_to_acescg(value)

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

# The way this works for now is that I take the LDConfig.ldr that comes with lDraw
# and convert it to a more easily digestible json, alongside aces conversion.
# However, some colors aren't quite accurate (mostly transparent colors are way too dark)
# therefore I have a brickini_colors.json that I manually fill up with better colors.
# If a color exists in that file, it overwrites the one coming from LDraw.
# For now it's just transparent colors, but might expand in the future...

color_dict = read_ld_config()
color_dict = update_to_brickini_colors(color_dict)

with open(ld_colors, 'w') as f:
    json.dump(color_dict, f, indent=4)