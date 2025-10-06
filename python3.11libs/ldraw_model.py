# pyright: reportMissingImports=false
from pathlib import Path
import hou
import re
import ldraw
import importlib

importlib.reload(ldraw)

class LdrawMpdHelper:
    def __init__(self, model):
        self.model = model

    def create_part(self, subfiles, key):
        '''Creates an unofficial part from an .mpd subfile.'''
        key_name = key.replace('s\\', '').replace('s/', '').replace('8\\', '').replace('8/', '').replace('48\\', '').replace('48/', '')
        file = Path()

        # loop through subfiles values for the key and find !LDRAW_ORG Line
        for line in subfiles[key]:
            line_split = line.split()

            if line_split[1] == '!LDRAW_ORG':
                part_type = line_split[2]
                
                if part_type == 'Unofficial_Part':
                    file = ldraw.p_u / key_name
                elif part_type == 'Unofficial_Subpart':
                    file = ldraw.ps_u / key_name
                elif part_type == 'Unofficial_Primitive':
                    file = ldraw.pr_u / key_name
                elif part_type == 'Unofficial_48_Primitive':
                    file = ldraw.pr48_u / key_name
                elif part_type == 'Unofficial_8_Primitive':
                    file = ldraw.pr8_u / key_name
                else:
                    file = ldraw.p_u / key_name
                break
            else:
                # if meta not present we just have to assume it's a part
                file = ldraw.p_u / key_name

        # write list to file
        if self.model.unofficial_file_rewrite or file.exists() == False:
            with open(file, 'w') as f:
                for line in subfiles[key]:
                    f.write(line)

    def find_subfiles(self):
        '''Returns a dict of subfiles from an mpd file.'''
        subfiles = dict()
        name = ''
        
        with open(self.model.file) as f:
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
    
    def build_subfiles(self, subfiles):
        # create unofficial directories if they don't exist
        dirs=[ldraw.ps_u, ldraw.pr48_u, ldraw.pr8_u]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

        #find dat subfile and create unofficial parts in ldraw lib
        for key in subfiles:
            if '.dat' in key or '.DAT' in key:
                self.create_part(subfiles, key)

class ldrawModel:
    def __init__(self, file, context_node=None):
        self.file = file
        self.main_model_name = self.file.stem
        self.main_model_name = ldraw.strip_special_characters(self.main_model_name)
        self.context_node = context_node
        self.unofficial_file_rewrite = False

    def build_context(self):
        if self.context_node is None:
            geo_node = hou.node('/obj').createNode('geo', 'brickini_ldraw_model_{}'.format(self.main_model_name))
        else:
            geo_node = hou.node(self.context_node.path() + '/sopcreate1/sopnet/create')
            # clean up existing nodes
            for child in geo_node.children():
                child.destroy()

            hou.node(self.context_node.path() + '/sopcreate1').parm('pathprefix').set('/geo/brickini_ldraw_model/m_' + self.main_model_name)

        return geo_node

    def build_network(self, geo_node):
        raise NotImplementedError
    
    def build_end_of_network(self, geo_node, last_node):
        i = last_node.createOutputNode('brickini_imperfections', 'brickini_imperfections1')
        o = i.createOutputNode('null', 'OUT')
        o.setRenderFlag(True)
        o.setDisplayFlag(True)
        geo_node.layoutChildren()

    def __call__(self):
        geo_node = self.build_context()
        last_node = self.build_network(geo_node)
        self.build_end_of_network(geo_node, last_node)

class LdrawStaticHelper():
    def __init__(self, model):
        self.model = model
        self.part_list = dict()

    def transform_part(self, node, m4, geo_node):
        '''Transforms the part according to the ldraw matrix and adjusts for the houdini coord sys.'''
        hxform = ldraw.xform_to_houdini()
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

    def place_part(self, color_code, part, geo_node):
        '''Places a part + color sop in the nodegraph.'''

        # add part as key to self.part_list dict if it doesn't exist
        if part not in self.part_list:
            self.part_list[part] = None

        part_name = part.replace('.dat', '').replace('.DAT', '')

        if not self.part_list[part]:
            part_sop_name = ldraw.strip_special_characters(part_name)
            part_sop_name = 'bldp_{0}_'.format(part_sop_name)              
            part_sop = geo_node.createNode('brickini_ldraw_part', part_sop_name)

            part_sop.parm('pack').set(1)
            part_sop.parm('print_handling').set(1)
            part_sop.parm('gap').set(1)
            part_sop.parm('part').set(part_name)

            self.part_list[part] = part_sop
        else:
            part_sop = self.part_list[part]

        # Deliberately not using the more convenient .createOutputNode() method as for some reason it's much slower than connecting it manually afterwards
        color_name = ldraw.get_color_name(color_code)
        material_sop_name = 'bm_{0}'.format(color_name)
        material_sop = geo_node.createNode('brickini_material', material_sop_name, run_init_scripts=True)
        material_sop.setInput(0, part_sop, 0)

        mat_parms = []
        all_parms = material_sop.parms()

        for a in all_parms:
            if 'material_' in a.name() and 'group' not in a.name():
                mat_parms.append(a)

        result_index = ldraw.find_value_index(mat_parms, color_code)
        
        material_sop.parm('material_group').set(result_index)

        # if color_code not valid parm value we fallback to 0 (black)
        try:
            mat_parms[result_index].set(color_code)
        except:
            mat_parms[result_index].set(0)

        return material_sop

class ldrawModelMpd(ldrawModel):
    def __init__(self, file, context_node=None):
        super().__init__(file, context_node)
        self.mpd_helper = LdrawMpdHelper(self)
        self.static_helper = LdrawStaticHelper(self)

    def build_mpd_model(self, subfiles, color_code, subfile, geo_node):
        '''Builds a model from an mpd file.'''
        t_list = []
        t_list_master = []
        color_group = color_code

        for line in subfiles[subfile]:
            if len(line) < 3:
                continue

            if line[0] == '1':
                line = line.split()
                part = ' '.join(line[14:])

                color_code = line[1]
                # to allow group colors penetrating through sub files
                if color_code == '16':
                    color_code = color_group

                if '.dat' in part or '.DAT' in part:
                    output = self.static_helper.place_part(color_code, part, geo_node)
                else:
                    t_list = self.build_mpd_model(subfiles, color_code, part, geo_node)
                    m = geo_node.createNode('merge', 'merge1')
                    for t in t_list:
                        m.setNextInput(t)
                    output = m

                m4 = ldraw.get_matrix(line)
                t = self.static_helper.transform_part(output, m4, geo_node)
                t_list_master.append(t)

        return(t_list_master)

    def build_network(self, geo_node):
        subfiles = self.mpd_helper.find_subfiles()
        self.mpd_helper.build_subfiles(subfiles)

        # find subfile that contains the main model
        # we assume it's the first one, but for safety we still check if there's one with 'main' in its name
        main_subfile = next(iter(subfiles))

        for key in subfiles:
            if 'main' in key.lower():
                main_subfile = key
                break

        # build model
        t_list_master = self.build_mpd_model(subfiles, '16', main_subfile, geo_node)

        last_node = geo_node.createNode('merge', 'merge1')
        for t in t_list_master:
            last_node.setNextInput(t)

        return last_node

class ldrawModelLdr(ldrawModel):
    def __init__(self, file, context_node=None):
        super().__init__(file, context_node)
        self.static_helper = LdrawStaticHelper(self)

    def build_ldr_model(self, geo_node):
        '''Builds a model from an ldr file.'''
        t_list_master = []

        with open(self.file) as f:
            for line in f:
                line = line.split()

                if len(line) < 3:
                    continue

                if line[0] == '1':
                    part = ' '.join(line[14:])

                    color_code = line[1]
                    output = self.static_helper.place_part(color_code, part, geo_node)

                    m4 = ldraw.get_matrix(line)
                    t = self.static_helper.transform_part(output, m4, geo_node)
                    t_list_master.append(t)

        return(t_list_master)

    def build_network(self, geo_node):
        # build model       
        t_list_master = self.build_ldr_model(geo_node)

        last_node = geo_node.createNode('merge', 'merge1')
        for t in t_list_master:
            last_node.setNextInput(t)

        return last_node

class ldrawModelDynamicShelf(ldrawModel):
    def build_network(self, geo_node):
        last_node = geo_node.createNode('brickini_ldraw_model', 'bldm_' + self.main_model_name)
        last_node.parm('ldrawfile').set(str(self.file))

        return last_node

class ldrawModelDynamic():
    def __init__(self, file, node):
        self.mpd_helper = LdrawMpdHelper(self)
        self.file = file
        self.file_type = file.suffix

        self.color_dict = ldraw.color_lib()
        self.material_group = ldraw.material_group()

        self.geo = node.geometry()

        self.unofficial_file_rewrite = False

    def transform_part_point(self, pt, m4):
        '''Transforms the part according to the ldraw matrix and adjusts for the houdini coord sys.'''
        m4_part = ldraw.xform_to_houdini()
        m4 = m4_part.inverted() * m4 * m4_part

        pt.setAttribValue("xform", m4.asTuple())

    def create_part_point(self, color_code, part, m4):
        '''Creates a point representing a part.'''

        part_name = part.lower()
        isdat = '.dat' in part_name
        if isdat:
            part_name = part_name.replace('.dat', '').replace('.DAT', '')
            part_name = part_name.replace(' ', '')

        part_point = self.geo.createPoint()
        material_type = self.material_group.index(self.color_dict[color_code]["category"])

        point_type = "part" if isdat else "subcomponent"
        part_point.setAttribValue("type", point_type)
        part_point.setAttribValue('part', part_name)
        part_point.setAttribValue('Cd', self.color_dict[color_code]["rgb"])
        part_point.setAttribValue('color_code', int(color_code))
        part_point.setAttribValue('material_type', material_type)

        self.transform_part_point(part_point, m4)

        return part_point

    def build_model_points(self):        
        self.geo.addAttrib(hou.attribType.Point, "type", "")
        self.geo.addAttrib(hou.attribType.Point, "part", "")
        self.geo.addAttrib(hou.attribType.Point, "Cd", hou.Vector3(1.0, 1.0, 1.0))
        self.geo.addAttrib(hou.attribType.Point, "xform", hou.Matrix4(1.0).asTuple())
        self.geo.addAttrib(hou.attribType.Point, "modelname", "")
        self.geo.addAttrib(hou.attribType.Point, 'color_code', 0)
        self.geo.addAttrib(hou.attribType.Point, 'material_type', 0)

        pattern = re.compile(r"0 FILE (.+)$") 

        with open(self.file) as f:
            model_name = ""
            for line in f:
                lineparts = line.split()

                if len(line) < 3:
                    continue

                match = re.search(pattern, line)
                if match:
                    model_name = match.group(1).lower().strip()

                # we only look for file references inside subcomponents in mpd files.
                if self.file_type == '.mpd' and 'ldr' not in model_name:
                    continue

                if line[0] == '1':
                    part = ' '.join(lineparts[14:])
                    part = part.replace('s\\', '').replace('s/', '').replace('8\\', '').replace('8/', '').replace('48\\', '').replace('48/', '')

                    color_code = lineparts[1]
                    m4 = ldraw.get_matrix(lineparts)
                    point = self.create_part_point(color_code, part, m4)
                    model_name = model_name.replace('.dat', '').replace('.DAT', '')
                    point.setAttribValue("modelname", model_name)

    def __call__(self):  
        if self.file_type == '.mpd':
            subfiles = self.mpd_helper.find_subfiles()
            self.mpd_helper.build_subfiles(subfiles)

        # build model
        self.build_model_points()

def main(mode=0, context_node=None):
    if context_node is None:
        file = hou.ui.selectFile(start_directory=None, title=None, collapse_sequences=False, file_type=hou.fileType.Any, pattern='*.ldr, *.l3b, *.mpd', default_value=None, multiple_select=False, image_chooser=None, chooser_mode=hou.fileChooserMode.Read, width=0, height=0)
    else:
        file = context_node.parm('ldraw_file').eval()
    file = hou.expandString(file)
    file = Path(file)
    
    file_type = file.suffix

    if file_type == '.mpd' and mode != 1:
        load_model = ldrawModelMpd(file, context_node)
    elif (file_type == '.ldr' or file_type == '.l3b') and mode != 1:
        load_model = ldrawModelLdr(file, context_node)
    elif (file_type == '.mpd' or file_type == '.ldr' or file_type == '.l3b') and mode == 1:
        load_model = ldrawModelDynamicShelf(file, context_node)
    elif file_type == '':
        return
    else:
        hou.ui.displayMessage('Please choose one of the following file types: ldr, l3b or mpd', buttons=('OK',), severity=hou.severityType.Error, default_choice=0, close_choice=-1, title='Wrong File Type', )
        return
    
    load_model()