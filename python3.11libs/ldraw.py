# pyright: reportMissingImports=false
from pathlib import Path
import hou
import re
import json

def ldraw_lib():
    '''Returns the path to the ldraw library. This is set as an environment variable in the houdini.env file.'''
    ldraw_lib = Path(hou.getenv('LDRAW_LIB'))
    return ldraw_lib

def resources():
    '''Returns the path to the resources folder.'''
    ldraw2houdini_path = Path(hou.getenv('LDRAW2HOUDINI'))
    resources = ldraw2houdini_path / 'resources'
    return resources

def color_lib():
    '''Returns a dict of ldraw colors.'''
    color_config = resources() / 'ld_colors.json'

    with open(color_config, 'r') as f:
        color_dict = json.load(f)
    return color_dict

# ldraw paths shortcuts
p = ldraw_lib() / 'parts'
ps = ldraw_lib() / 'parts' / 's'
pr = ldraw_lib() / 'p'
pr48 = ldraw_lib() / 'p' / '48'
pr8 = ldraw_lib() / 'p' / '8'

p_u = ldraw_lib() / 'UnOfficial' / 'parts'
ps_u = ldraw_lib() / 'UnOfficial' / 'parts' / 's'
pr_u = ldraw_lib() / 'UnOfficial' / 'p'
pr48_u = ldraw_lib() / 'UnOfficial' / 'p' / '48'
pr8_u = ldraw_lib() / 'UnOfficial' / 'p' / '8'
pr_l2h = resources() / 'ldraw' / 'p'

def material_group():
    """Return a list of unique material categories in order of first appearance."""
    result_list = []
    # Iterate over the color data
    for color_info in color_lib().values():
        category = color_info['category']

        # Check if the category is new
        if category not in result_list:
            result_list.append(category)

    return result_list

def get_matrix(line):
    '''Returns a houdini matrix from a line of an ldraw file.'''
    line = line[2:14]
    l = list(map(float, line))
    m4 = hou.Matrix4(((l[3], l[6], l[9], 0), (l[4], l[7], l[10], 0), (l[5], l[8], l[11], 0), (l[0], l[1], l[2], 1)))
    return m4

def strip_special_characters(input_string):
    return re.sub('[^0-9a-zA-Z_-]+', '', input_string)

def find_value_index(list_of_lists, search_value):
    for index, sublist in enumerate(list_of_lists):
        if search_value in sublist.menuItems():
            return index
    return 0 # if not found we fallback to solid material group

def get_color_name(color_code):
    entry = color_lib().get(color_code)
    if entry:
        color_name = entry.get('name')
    else:
        color_name = 'Not_Found'
    return color_name

def xform_to_houdini():
    '''
    compensate for houdini coord sys
    convert from LDU to metric (1 LDU = 0.4mm), however we multiply by 10,
    so a 1x1 brick is 8 cm wide and a minifigure is therefore (38.4 cm tall)
    hopefully this is the right balance to get stable sims and stay in the safe floating point zone
    '''
    transform_dict = dict()
    transform_dict['rotate'] = (180, 0, 0)
    transform_dict['scale'] = (0.004, 0.004, 0.004)
    return hou.hmath.buildTransform(transform_dict, transform_order="srt", rotate_order="xyz")

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