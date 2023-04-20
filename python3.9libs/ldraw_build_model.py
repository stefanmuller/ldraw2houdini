import hou
from pathlib import Path
import re
import brickini

color_dict = brickini.color_lib()

def get_color(color):
    try:
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

def build_model():
    file = hou.ui.selectFile(start_directory=None, title=None, collapse_sequences=False, file_type=hou.fileType.Any, pattern=None, default_value=None, multiple_select=False, image_chooser=None, chooser_mode=hou.fileChooserMode.Read, width=0, height=0)
    t_list = []

    model_name = Path(file).stem
    model_name = strip_special_characters(model_name)
    model_name = 'ldraw_model_{}'.format(model_name)
    print('building {}...'.format(model_name))

    model = hou.node('/obj').createNode('geo', model_name)

    with open(file) as f:

        for line in f:
            line = line.split()

            if len(line) < 3:
                continue

            if line[0] == '1':
                part = line[14]
                # print (part)

                color_code = line[1]
                color = get_color(color_code)

                m4 = get_matrix(line)
                # compensate for houdini coord sys
                m4_part = hou.hmath.buildRotate(-180, 0, 0)
                m4 = m4*m4_part

                tr = m4.explode()
                part = part.replace('.dat', '')
                part = part.replace('.DAT', '')
                part_sop_name = strip_special_characters(part)
                part_sop_name = 'part_{0}_1'.format(part_sop_name)                
                part_sop = model.createNode('brickini_ldraw_part', part_sop_name)

                print(part_sop_name)

                part_sop.parm('part').set(part)
                part_sop.parm('colorr').set(color[0])
                part_sop.parm('colorg').set(color[1])
                part_sop.parm('colorb').set(color[2])

                t = part_sop.createOutputNode('xform')
                t.parm('prexform_tx').set(tr.get('translate')[0])
                t.parm('prexform_ty').set(tr.get('translate')[1])
                t.parm('prexform_tz').set(tr.get('translate')[2])
                t.parm('prexform_rx').set(tr.get('rotate')[0])
                t.parm('prexform_ry').set(tr.get('rotate')[1])
                t.parm('prexform_rz').set(tr.get('rotate')[2])
                
                # compensate for houdini coord sys
                t.parm('rx').set(180)

                t_list.append(t)


    m = model.createNode('merge')
    for t in t_list:
        m.setNextInput(t)

    o = m.createOutputNode('output')
    o.setRenderFlag(True)
    o.setDisplayFlag(True)
    model.layoutChildren()

    return


