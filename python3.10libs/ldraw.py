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
    this_file = Path(__file__).resolve()
    resources = this_file.parent.parent / 'resources'
    return resources

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

part_list = dict()

def color_lib():
    '''Returns a dict of ldraw colors.'''
    color_config = resources() / 'ld_colors.json'

    with open(color_config, 'r') as f:
        color_dict = json.load(f)
    return color_dict

color_dict = color_lib()

def get_matrix(line):
    '''Returns a houdini matrix from a line of an ldraw file.'''
    line = line[2:14]
    l = list(map(float, line))
    m4 = hou.Matrix4(((l[3], l[6], l[9], 0), (l[4], l[7], l[10], 0), (l[5], l[8], l[11], 0), (l[0], l[1], l[2], 1)))
    return m4

def strip_special_characters(input_string):
    return re.sub('[^0-9a-zA-Z_-]+', '', input_string)


def find_subfiles(file):
    '''Returns a dict of subfiles from an mpd file.'''
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

def find_value_index(list_of_lists, search_value):
    for index, sublist in enumerate(list_of_lists):
        if search_value in sublist.menuItems():
            return index
    return 0 # if not found we fallback to solid material group

def get_color_name(color_code):
    _color_lib = color_lib()
    entry = _color_lib.get(color_code)
    if entry:
        color_name = entry.get('name')
    else:
        color_name = 'Not_Found'
    return color_name

def place_part(color_code, part, geo_node):
    '''Places a part + color sop in the nodegraph.'''

    # add part as key to part_list dict if it doesn't exist
    if part not in part_list:
        part_list[part] = None

    part_name = part.replace('.dat', '').replace('.DAT', '')

    if not part_list[part]:
        part_sop_name = strip_special_characters(part_name)
        part_sop_name = 'bldp_{0}_'.format(part_sop_name)              
        part_sop = geo_node.createNode('brickini_ldraw_part', part_sop_name)

        part_sop.parm('part').set(part_name)
        part_sop.parm('pack').set(1)
        part_sop.parm('gap').set(1)

        part_list[part] = part_sop
    else:
        part_sop = part_list[part]

    # Deliberately not using the more convenient .createOutputNode() method as for some reason it's much slower than connecting it manually afterwards
    color_name = get_color_name(color_code)
    material_sop_name = 'bm_{0}'.format(color_name)
    material_sop = geo_node.createNode('brickini_material', material_sop_name, run_init_scripts=True)
    material_sop.setInput(0, part_sop, 0)

    mat_parms = []
    all_parms = material_sop.parms()

    for a in all_parms:
        if 'material_' in a.name() and 'group' not in a.name():
            mat_parms.append(a)

    result_index = find_value_index(mat_parms, color_code)
    
    material_sop.parm('material_group').set(result_index)

    # if color_code not valid parm value we fallback to 0 (black)
    try:
        mat_parms[result_index].set(color_code)
    except:
        mat_parms[result_index].set(0)

    return material_sop

def xform_to_houdini():
    # compensate for houdini coord sys
    # convert from LDU to metric (1 LDU = 0.4mm), however we multiply by 10,
    # so a 1x1 brick is 8 cm wide and a minifigure is therefore (38.4 cm tall)
    # hopefully this is the right balance to get stable sims and stay in the safe floating point zone
    transform_dict = dict()
    transform_dict['rotate'] = (-180, 0, 0)
    transform_dict['scale'] = (0.004, 0.004, 0.004)
    return hou.hmath.buildTransform(transform_dict, transform_order="srt", rotate_order="xyz")

def transform_part(node, m4, geo_node):
    '''Transforms the part according to the ldraw matrix and adjusts for the houdini coord sys.'''
    hxform = xform_to_houdini()
    m4 = hxform.inverted() * m4 * hxform
    tr = m4.explode()

    t = geo_node.createNode('xform', 'transform1', run_init_scripts=False)
    t.setInput(0, node, 0)
    t.parm('prexform_tx').set(tr.get('translate')[0])
    t.parm('prexform_ty').set(tr.get('translate')[1])
    t.parm('prexform_tz').set(tr.get('translate')[2])
    t.parm('prexform_rx').set(tr.get('rotate')[0])
    t.parm('prexform_ry').set(tr.get('rotate')[1])
    t.parm('prexform_rz').set(tr.get('rotate')[2])
    t.parm('prexform_sx').set(tr.get('scale')[0])
    t.parm('prexform_sy').set(tr.get('scale')[1])
    t.parm('prexform_sz').set(tr.get('scale')[2])

    return t

def transform_part_point(pt, m4):
    '''Transforms the part according to the ldraw matrix and adjusts for the houdini coord sys.'''
    m4_part = xform_to_houdini()
    m4 = m4_part.inverted() * m4 * m4_part

    pt.setAttribValue("xform", m4.asTuple())

def create_part_point(geo, color_code, part, m4):
    '''Creates a point representing a part.'''

    part_name = part.lower()
    isdat = '.dat' in part_name
    if isdat:
        part_name = part_name.replace('.dat', '').replace('.DAT', '')
        part_name = part_name.replace(' ', '')
        # part_name = part

    part_point = geo.createPoint()

    point_type = "part" if isdat else "subcomponent"
    part_point.setAttribValue("type", point_type)
    part_point.setAttribValue('part', part_name)
    part_point.setAttribValue('Cd', color_dict[color_code]["rgb"])

    transform_part_point(part_point, m4)

    return part_point

def build_mpd_model(subfiles, subfile, geo_node):
    '''Builds a model from an mpd file.'''
    t_list = []
    t_list_master = []

    for line in subfiles[subfile]:
        if len(line) < 3:
            continue

        if line[0] == '1':
            line = line.split()
            part = ' '.join(line[14:])

            color_code = line[1]

            if '.dat' in part or '.DAT' in part:
                output = place_part(color_code, part, geo_node)
            else:
                t_list = build_mpd_model(subfiles, part, geo_node)
                m = geo_node.createNode('merge', 'merge1')
                for t in t_list:
                    m.setNextInput(t)
                output = m

            m4 = get_matrix(line)
            t = transform_part(output, m4, geo_node)
            t_list_master.append(t)

    return(t_list_master)

def build_ldr_model(file, geo_node):
    '''Builds a model from an ldr file.'''
    t_list_master = []

    with open(file) as f:
        for line in f:
            line = line.split()

            if len(line) < 3:
                continue

            if line[0] == '1':
                part = ' '.join(line[14:])

                color_code = line[1]
                output = place_part(color_code, part, geo_node)

                m4 = get_matrix(line)
                t = transform_part(output, m4, geo_node)
                t_list_master.append(t)

    return(t_list_master)

def build_model_points(geo, file):
    geo.addAttrib(hou.attribType.Point, "type", "")
    geo.addAttrib(hou.attribType.Point, "part", "")
    geo.addAttrib(hou.attribType.Point, "Cd", hou.Vector3(1.0, 1.0, 1.0))
    geo.addAttrib(hou.attribType.Point, "xform", hou.Matrix4(1.0).asTuple())
    geo.addAttrib(hou.attribType.Point, "modelname", "")

    with open(file) as f:
        model_name = ""
        for line in f:
            lineparts = line.split()

            if len(line) < 3:
                continue

            pattern = r"0 FILE (.+)$"

            # Use re.search to find the match

            match = re.search(pattern, line)
            # Check if a match is found
            if match:
                model_name = match.group(1).lower().strip()

            if line[0] == '1':
                part = ' '.join(lineparts[14:])

                color_code = lineparts[1]
                m4 = get_matrix(lineparts)
                point = create_part_point(geo, color_code, part, m4)
                model_name = model_name.replace('.dat', '').replace('.DAT', '')
                point.setAttribValue("modelname", model_name)

def create_part(subfiles, key):
    '''Creates an unofficial part from an .mpd subfile.'''
    key_name = key.replace('s\\', '').replace('s/', '').replace('8\\', '').replace('8/', '').replace('48\\', '').replace('48/', '')
    file = Path()

    # loop through subfiles values for the key and find !LDRAW_ORG Line
    for line in subfiles[key]:
        line_split = line.split()

        if line_split[1] == '!LDRAW_ORG':
            part_type = line_split[2]
            
            if part_type == 'Unofficial_Part':
                file = p_u / key_name
            elif part_type == 'Unofficial_Subpart':
                file = ps_u / key_name
            elif part_type == 'Unofficial_Primitive':
                file = pr_u / key_name
            elif part_type == 'Unofficial_48_Primitive':
                file = pr48_u / key_name
            elif part_type == 'Unofficial_8_Primitive':
                file = pr8_u / key_name
            else:
                file = p_u / key_name
            break
        else:
            # if meta not present we just have to assume it's a part
            file = p_u / key_name

            # if file already exists, delete it
            if file.exists():
                file.unlink()

    for line in subfiles[key]:
        # write list to file
        with open(file, 'a') as f:
            f.write(line)

def build_subfiles(subfiles):
    # create unofficial directories if they don't exist
    dirs=[ps_u, pr48_u, pr8_u]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    #find dat subfile and create unofficial parts in ldraw lib
    for key in subfiles:
        if '.dat' in key or '.DAT' in key:
            create_part(subfiles, key)

def main():
    '''Main function.'''
    file = hou.ui.selectFile(start_directory=None, title=None, collapse_sequences=False, file_type=hou.fileType.Any, pattern=None, default_value=None, multiple_select=False, image_chooser=None, chooser_mode=hou.fileChooserMode.Read, width=0, height=0)
    file = hou.expandString(file)
    file = Path(file)
    model_master_name = file.stem
    model_master_name = strip_special_characters(model_master_name)
    model_master_name = 'ldraw_model_{}'.format(model_master_name)
    print('building {} ...'.format(model_master_name))

    # depending on suffix either process as mpd (multi part document) or ldr
    file_type = file.suffix

    if file_type == '.mpd':
        # create sop network
        geo_node = hou.node('/obj').createNode('geo', model_master_name)

        subfiles = find_subfiles(file)

        build_subfiles(subfiles)

        #find subfile that contains the main model
        for key in subfiles:
            if 'main' in key.lower():
                main_subfile = key
            else:
                # if main is not present, we just assume the first FILE is the main model.
                main_subfile = next(iter(subfiles))

        # build model
        t_list_master = build_mpd_model(subfiles, main_subfile, geo_node)

    elif file_type == '.ldr' or file_type == '.l3b':
        # create sop network
        geo_node = hou.node('/obj').createNode('geo', model_master_name)

        # build model
        t_list_master = build_ldr_model(file, geo_node)

    else:
        hou.ui.displayMessage('Please choose one of the following file types: ldr, l3b or mpd', buttons=('OK',), severity=hou.severityType.Error, default_choice=0, close_choice=-1, title='Wrong File Type', )
        return

    m = geo_node.createNode('merge', 'merge1')
    for t in t_list_master:
        m.setNextInput(t)

    i = m.createOutputNode('brickini_imperfections', 'brickini_imperfections1')
    o = i.createOutputNode('output', 'output1')
    o.setRenderFlag(True)
    o.setDisplayFlag(True)
    geo_node.layoutChildren()
