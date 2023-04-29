# pyright: reportMissingImports=false
from pathlib import Path
import hou
import re
import json
import random

def ldraw_lib():
    ldraw_lib = Path(hou.getenv('LDRAW_LIB'))
    return ldraw_lib

p = ldraw_lib() / 'parts'
ps = ldraw_lib() / 'parts' / 's'
pr = ldraw_lib() / 'p'
pr48 = ldraw_lib() / 'p' / '48'
pr8 = ldraw_lib() / 'p' / '8'

p_u = ldraw_lib() / 'unofficial' / 'parts'
ps_u = ldraw_lib() / 'unofficial' / 'parts' / 's'
pr_u = ldraw_lib() / 'unofficial' / 'p'
pr48_u = ldraw_lib() / 'unofficial' / 'p' / '48'
pr8_u = ldraw_lib() / 'unofficial' / 'p' / '8'

def color_lib():
    this_file = Path(__file__).resolve()
    color_config = this_file.parent.parent / 'resources' / 'ld_colors.json'

    with open(color_config, 'r') as f:
        color_dict = json.load(f)
    return color_dict

def get_color(color):
    try:
        color_dict = color_lib()
        color = color_dict[color]
    except:
        color = hou.Vector3(1, 0, 0.5)
    return color

def get_matrix(line):
    line = line[2:14]
    l = list(map(float, line))
    m4 = hou.Matrix4(((l[3], l[6], l[9], 0), (l[4], l[7], l[10], 0), (l[5], l[8], l[11], 0), (l[0], l[1], l[2], 1)))
    return m4

def strip_special_characters(input_string):
    return re.sub('[^0-9a-zA-Z_-]+', '', input_string)

# create a dict for each subfile
def find_subfiles(file):
    subfiles = dict()
    name = ''
    
    with open(file) as f:
        for line in f:
            line_split = line.split()

            if len(line_split) < 3:
                continue

            if line_split[0] == '0' and line_split[1] == 'FILE':
                # we remove any spaces for filenames
                # add name as the key to the dict
                name = ''.join(line_split[2:])                
                subfiles[name] = []
            
            if line_split[0] == '0' or line_split[0] == '1' or line_split[0] == '3' or line_split[0] == '4':
                # we reconstruct the line but remove spaces from subfile references
                # add line to the value of the key name
                part = ''.join(line_split[14:])
                line = ' '.join(line_split[:14]) + ' ' + part + '\n'
                subfiles[name].append(line)                 

    return subfiles

def place_part(color, part, part_list, geo_node):

    # create random int for seed
    seed = random.randint(0, 100000)

    # add part as key to part_list dict if it doesn't exist
    if part not in part_list:
        part_list[part] = None

    part_name = part.replace('.dat', '').replace('.DAT', '')

    if not part_list[part]:
        part_sop_name = strip_special_characters(part_name)
        part_sop_name = 'part_{0}_1'.format(part_sop_name)              
        part_sop = geo_node.createNode('brickini_ldraw_part', part_sop_name)

        part_sop.parm('part').set(part_name)
        part_sop.parm('colorr').set(color[0])
        part_sop.parm('colorg').set(color[1])
        part_sop.parm('colorb').set(color[2])
        part_sop.parm('pack').set(1)
        part_sop.parm('seed').set(seed)

        part_list[part] = part_sop
    else:
        part_sop = part_list[part]

    color_sop = part_sop.createOutputNode('color')
    color_sop.parm('colorr').set(color[0])
    color_sop.parm('colorg').set(color[1])
    color_sop.parm('colorb').set(color[2])

    return color_sop

def transform_part(node, m4):
    # compensate for houdini coord sys
    # convert from LDU to metric (1 LDU = 0.4mm), however we multiply by 100,
    # so 1 brick is 0.8m wide and a minifigure is therefore *very roughly* human scale (3.84 meters tall)
    # m4_part = hou.hmath.buildRotate(-180, 0, 0)
    transform_dict = dict()
    transform_dict['rotate'] = (-180, 0, 0)
    transform_dict['scale'] = (0.04, 0.04, 0.04)
    m4_part = hou.hmath.buildTransform(transform_dict, transform_order="srt", rotate_order="xyz")
    m4 = m4*m4_part
    tr = m4.explode()

    t = node.createOutputNode('xform')
    t.parm('prexform_tx').set(tr.get('translate')[0])
    t.parm('prexform_ty').set(tr.get('translate')[1])
    t.parm('prexform_tz').set(tr.get('translate')[2])
    t.parm('prexform_rx').set(tr.get('rotate')[0])
    t.parm('prexform_ry').set(tr.get('rotate')[1])
    t.parm('prexform_rz').set(tr.get('rotate')[2])
    
    # compensate for houdini coord sys
    t.parm('rx').set(180)
    return t


def build_mpd_model(subfiles, subfile, geo_node):
    t_list = []
    t_list_master = []
    part_list = dict()

    for line in subfiles[subfile]:
        if len(line) < 3:
            continue

        if line[0] == '1':
            line = line.split()
            part = ' '.join(line[14:])
            print(part)

            color_code = line[1]
            color = get_color(color_code)

            if '.dat' in part or '.DAT' in part:
                output = place_part(color, part, part_list, geo_node)

            else:
                t_list = build_mpd_model(subfiles, part, geo_node)
                m = geo_node.createNode('merge')
                for t in t_list:
                    m.setNextInput(t)
                output = m

            m4 = get_matrix(line)
            t = transform_part(output, m4)
            t_list_master.append(t)

    return(t_list_master)

def build_ldr_model(file, geo_node):
    t_list_master = []
    part_list = dict()

    with open(file) as f:
        for line in f:
            line = line.split()

            if len(line) < 3:
                continue

            if line[0] == '1':
                part = ' '.join(line[14:])
                print(part)

                color_code = line[1]
                color = get_color(color_code)
                output = place_part(color, part, part_list, geo_node)

                m4 = get_matrix(line)
                t = transform_part(output, m4)
                t_list_master.append(t)

    return(t_list_master)

def create_part(subfiles, key):
    key_name = key.replace('s\\', '').replace('s/', '').replace('8\\', '').replace('8/', '').replace('48\\', '').replace('48/', '')
    file = Path()

    # loop through subfiles values for the key and find !LDRAW_ORG Line
    for line in subfiles[key]:
        line_split = line.split()

        if line_split[1] == '!LDRAW_ORG':
            part_type = line_split[2]
            
            if part_type == 'Unofficial_Part':
                file = p_u / key_name
            if part_type == 'Unofficial_Subpart':
                file = ps_u / key_name
            if part_type == 'Unofficial_Primitive':
                file = pr_u / key_name
            if part_type == 'Unofficial_48_Primitive':
                file = pr48_u / key_name
            if part_type == 'Unofficial_8_Primitive':
                file = pr8_u / key_name

            # if file already exists, delete it
            if file.exists():
                file.unlink()

    for line in subfiles[key]:
        # write list to file
        with open(file, 'a') as f:
            f.write(line)

def main():
    file = hou.ui.selectFile(start_directory=None, title=None, collapse_sequences=False, file_type=hou.fileType.Any, pattern=None, default_value=None, multiple_select=False, image_chooser=None, chooser_mode=hou.fileChooserMode.Read, width=0, height=0)
    file = Path(file)
    model_master_name = file.stem
    model_master_name = strip_special_characters(model_master_name)
    model_master_name = 'ldraw_model_{}'.format(model_master_name)
    print('building {} ...'.format(model_master_name))

    # create unofficial directories if they don't exist
    dirs=[ps_u, pr48_u, pr8_u]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # create sop network
    geo_node = hou.node('/obj').createNode('geo', model_master_name)

    # depending on suffix either process as mpd (multi part document) or ldr
    file_type = file.suffix

    if file_type == '.mpd':
        subfiles = find_subfiles(file)

        #find dat subfile and create unofficial parts in ldraw lib
        for key in subfiles:
            if '.dat' in key or '.DAT' in key:
                create_part(subfiles, key)

        #find subfile that contains the main model
        for key in subfiles:
            if 'main' in key:
                main_subfile = key
            
        t_list_master = build_mpd_model(subfiles, main_subfile, geo_node)

    elif file_type == '.ldr':
        t_list_master = build_ldr_model(file, geo_node)

    m = geo_node.createNode('merge')
    for t in t_list_master:
        m.setNextInput(t)

    o = m.createOutputNode('output')
    o.setRenderFlag(True)
    o.setDisplayFlag(True)
    geo_node.layoutChildren()