# pyright: reportMissingImports=false
from pathlib import Path, PureWindowsPath
import ldraw
import hou
import json
import re

class ldrawPart:
    def __init__(self, node, parms):
        self.ldraw_lib = ldraw.ldraw_lib()
        self.color_dict = ldraw.color_lib()
        self.default_color = hou.Vector3(1, 1, 1)
        self.ldraw_cache = hou.getenv('LDRAW_CACHE')
 
        if self.ldraw_cache != 1 and self.ldraw_cache != "1":
            self.ldraw_cache = 0
        else:
            self.ldraw_cache = 1

        # python sop
        self.node = node

        # store all the parms
        self.parm_part = parms.get('parm_part')
        self.parm_highres = parms.get('parm_highres')
        self.parm_stud = parms.get('parm_stud')
        self.parm_pack = parms.get('parm_pack')
        self.parm_print = parms.get('parm_print')
        self.parm_edges = parms.get('parm_edges')
        self.parm_material_group = parms.get('parm_material_group')
        self.parm_material = parms.get('parm_material')

        # store this geo
        self.geo = self.node.geometry()

        # write attributes
        self.geo.addAttrib(hou.attribType.Global, 'cache', self.ldraw_cache)

        self.geo.addArrayAttrib(hou.attribType.Global, 'part_color', hou.attribData.Float)
        self.geo.setGlobalAttribValue('part_color', self.color_dict[str(self.parm_material)]['rgb'])

        self.geo.addAttrib(hou.attribType.Global, 'name', '')
        self.geo.setGlobalAttribValue('name', 'p_' + self.parm_part)

        texture_path = self.ldraw_lib / 'textures' / str(self.parm_part + '_basecolor.png')

        if self.parm_print == 2:
            self.geo.addAttrib(hou.attribType.Global, 'print', '')
            self.geo.setGlobalAttribValue('print', str(texture_path))

        if not self.parm_pack:
            self.geo.addAttrib(hou.attribType.Vertex, 'Cd', self.default_color)
            self.geo.addAttrib(hou.attribType.Vertex, 'material_type', self.parm_material_group)
        else:
            self.geo.addAttrib(hou.attribType.Vertex, 'Cd2', self.default_color)
            self.geo.addAttrib(hou.attribType.Vertex, 'color_mode', 0)

        self.geo.addAttrib(hou.attribType.Point, 'info', '')
        self.geo.addAttrib(hou.attribType.Vertex, 'color_code', 0)

    def part_properties(self, property):
        properties = ldraw.resources() / 'part_properties.json'
        with open(properties) as f:
            data = json.load(f)
        property = data[property]

        return property

    def extract_points(self, line, vertnum, winding):
        '''extract the vert positions and put them into the correct winding order'''
        line = line[2:]
        line = list(map(float, line))
        points = []
        for i in range(vertnum):
            points.append((line[i*3],line[i*3+1],line[i*3+2]))

        # reverse point order according to winding variable
        if winding == 'CCW':
            if vertnum == 4:
                points = (points[0], points[3], points[2], points[1])
            if vertnum == 3:
                points = (points[0], points[2], points[1])

        return points

    def create_poly(self, points, m4, color, static_color, color_code, info):
        '''create geometry and write info and color attributes'''
        poly = self.geo.createPolygon()
        for position in points:
            point = self.geo.createPoint()
            point.setPosition(position)
            v = poly.addVertex(point)

            if len(points) > 2:
                v.setAttribValue('color_code', int(color_code))
                point.setAttribValue('info', info)

                if not self.parm_pack:
                    v.setAttribValue('Cd', color)
                else:
                    v.setAttribValue('Cd2', color)
                    if static_color:
                        v.setAttribValue('color_mode', 1)
            else:
                poly.setIsClosed(False)
        


        self.geo.transformPrims([poly], m4)
        return poly

    def determine_winding(self, winding_group, m4_group, invert_next):
        '''
        this function determines winding order
        invert winding again if orientation matrix is reversed (negative determinant)
        cancel out inversion if INVERTNEXT statement is found before subpart reference
        '''
        m4_group_det = m4_group.determinant()
        if m4_group_det < 0:
            if winding_group == 'CCW':
                winding_group = 'CW'
            else:
                winding_group = 'CCW'

        if invert_next == True:
            if winding_group == 'CCW':
                winding_group = 'CW'
            else:
                winding_group = 'CCW'
        return winding_group

    def hex_to_rgb(self, hex_value):
        # Convert hex to decimal RGB values
        decimal_r = int(hex_value[0:2], 16)
        decimal_g = int(hex_value[2:4], 16)
        decimal_b = int(hex_value[4:6], 16)

        # Convert decimal RGB to float
        float_r = (decimal_r / 255) ** 2.2
        float_g = (decimal_g / 255) ** 2.2
        float_b = (decimal_b / 255) ** 2.2

        # Return as list
        return [float_r, float_g, float_b]

    def get_color(self, color, color_group):
        '''
        get color from ld color json
        16 is a special code, the color is determined by the referenced dat file
        '''
        static_color = False
        color_code = '16'
        if color == '16':
            if color_group == '16':
                color = self.color_dict[str(self.parm_material)]['rgb']

            else:
                color_code = color_group
                color = self.color_dict[color_group]['rgb']
                static_color = True
        else:
            # if x in color it's a direct color that looks like this: 0x2995220
            # and we need to convert it manually
            if 'x' in color:
                color = self.hex_to_rgb(color[3:8])
                color_code = 0
                static_color = True
            else:
                try:
                    color_code = color
                    color = self.color_dict[color]['rgb']
                    static_color = True
                except:
                    color = hou.Vector3(1, 0, 0.5)
        return color, static_color, color_code


    def path_resolve(self, part):
        '''
        find part in ldraw lib, this turned a bit into a beast, because the file format specifications
        aren't very strict. This function could probably be much more elegant.    
        '''
        part = PureWindowsPath(part)
        part = Path(part)
        part = str(part)
        part_lower = str(part).lower()
        part = part.replace(' ','')

        # creating a list, with the part as it's written in the file and fully lowercase
        part_list=(part_lower, part)

        # looping over the list, first trying to find the part as is
        # if unsuccesful, we try again fully lowercase
        for p in part_list:
            part_dir = ldraw.p / p

            if not part_dir.exists():
                part_dir = ldraw.ps / p
                if not part_dir.exists():
                    part_dir = ldraw.pr / p
                    if part_dir.exists():
                        if self.parm_highres:
                            highres_part = ldraw.pr48 / p
                            if  highres_part.exists():
                                part_dir = highres_part

                    else:
                        part_dir = ldraw.p_u / p
                        if not part_dir.exists():
                            part_dir = ldraw.ps_u / p
                            if not part_dir.exists():
                                part_dir = ldraw.pr_u / p
                                if part_dir.exists():
                                    if self.parm_highres:
                                        highres_part = ldraw.pr48_u / p
                                        if  highres_part.exists():
                                            part_dir = highres_part
                                else:
                                    part_dir = ldraw.pr_l2h / p

            if part_dir.exists():
                # if we found the part, break, otherwise we try again with everything lowercase
                break

        if not part_dir.exists():
            part_dir = ldraw.pr_l2h / 'box-part-not-found.dat'

        return part_dir

    
    def read_part(self, part, m4, winding, color_code, info):
        '''
        recursive function that reads the part and then either creates
        lines, tris, quads or reads subparts inside the part
        '''
        if not part.exists():
            return

        with open(part) as f:
            poly_list=[]
            invert_next = False
            winding_sub = winding
            color_group = color_code
            info_group = info
            static_color = False

            for line in f:
                line = line.split()
                winding_group = winding

                if len(line) < 3:
                    continue

                # meta: checking for winding order and inversion
                elif line[0] == '0':
                    # invert winding according to header
                    if line[1] == 'BFC' and line[2] == 'CERTIFY':
                        if line[3] == 'CW':
                            if winding == 'CCW':
                                winding_sub = 'CW'
                            else:
                                winding_sub = 'CCW'

                    # subpart that we'll find in the line after this one needs to be inversed
                    elif line[1] == 'BFC' and line[2] == 'INVERTNEXT':
                        invert_next = True
                        # print ('we invert')

                # part/prim reference
                if line[0] == '1':
                    part = ' '.join(line[14:])

                    # load special stud-instance which is just a helper prim to be able to instance the actual stud geo in the hda network
                    if self.parm_stud:
                        if part == 'stud.dat':
                            part = 'stud-instance.dat'
                            info_group = 'stud'
                        elif part == 'stud2.dat':
                            part = 'stud-instance.dat'
                            info_group = 'stud2'
                        else:
                            info_group = info

                    if part == 'logo4.dat':
                        info_group = 'logo'

                    # we only process edges if checked.
                    # It's needed for beveling and consistent primitive count
                    if not self.parm_edges:
                        if 'edge' in part:
                            continue

                    color_code = line[1]
                    # to allow group colors penetrating through sub files
                    if color_code == '16':
                        color_code = color_group

                    part = self.path_resolve(part)

                    if not part.exists():
                        break

                    m4_group = ldraw.get_matrix(line)

                    winding_group = self.determine_winding(winding_group, m4_group, invert_next)
                    invert_next = False

                    poly_list_sub = self.read_part(part, m4_group, winding_group, color_code, info_group)
                    self.geo.transformPrims(poly_list_sub, m4)
                    poly_list.extend(poly_list_sub)

                # tri
                elif line[0] == '3':
                    pass
                    color, static_color, color_code = self.get_color(line[1], color_group)
                    points = self.extract_points(line, 3, winding_sub)
                    if info != 'print' or (info == 'print' and color_code != '16'):
                        poly = self.create_poly(points, m4, color, static_color, color_code, info)
                        poly_list.append(poly)

                # quad
                elif line[0] == '4':
                    pass
                    color, static_color, color_code = self.get_color(line[1], color_group)
                    points = self.extract_points(line, 4, winding_sub)
                    if info != 'print' or (info == 'print' and color_code != '16'):
                        poly = self.create_poly(points, m4, color, static_color, color_code, info)
                        poly_list.append(poly)

                # lines
                if self.parm_edges and info == 'base':            
                    if line[0] == '2':
                        color = [0,0,0]
                        static_color = False
                        points = self.extract_points(line, 2, winding_sub)
                        poly = self.create_poly(points, m4, color, static_color, color_code, '')
                        poly_list.append(poly)
                    

        return poly_list

    def set_vertex_attribute(self, attribute, value, prim_list=[]):
        prims = self.geo.iterPrims()
        for p in prims:
            if p.number() in prim_list or not prim_list:
                prim_vertices = p.vertices()
                for v in prim_vertices:
                    v.setAttribValue(attribute, value) 

    def convert_houdini_list(self, prim_string):
        '''
        converts a houdini list that looks like this: '1-3 6 9-12' into a numbered list
        '''
        prim_list = []
        for part in prim_string.split():
            if '-' in part:
                start, end = map(int, part.split('-'))
                prim_list.extend(range(start, end + 1))
            else:
                prim_list.append(int(part))
        return prim_list

    def __call__(self):
        # print handling
        # load brick as set in parm parameter by default
        # load base brick if mode is set to separate and only keep print geo from actual brick
        # load base brick if mode is set to texture and we create uvs in the hda
        base_part = self.parm_part
        print_str = re.search('[a-zA-Z]+.*', self.parm_part)

        if print_str != None:
            print_str = print_str.group()
            base_part = self.parm_part.replace(print_str, '')

        if self.parm_print > 0 and print_str != None:
            if self.parm_print == 1:
                part_path = self.path_resolve(self.parm_part + '.dat')
                part_geo_print = self.read_part(part_path, hou.hmath.identityTransform(), 'CCW', '16', 'print')

            self.parm_part = base_part

        part_path = self.path_resolve(self.parm_part + '.dat')
        part_geo = self.read_part(part_path, hou.hmath.identityTransform(), 'CCW', '16', 'base')

        # adjust for houdini coord system
        transform_dict = dict()
        transform_dict['rotate'] = (180, 0, 0)
        transform_dict['scale'] = (0.004, 0.004, 0.004)
        m4_part = hou.hmath.buildTransform(transform_dict, transform_order='srt', rotate_order='xyz')

        try:
            part_geo.extend(part_geo_print)
        except:
            pass

        self.geo.transformPrims(part_geo, m4_part)

        # additional part properties

        # slope attribute
        if base_part in self.part_properties('slopes'):
            self.geo.addAttrib(hou.attribType.Global, 'slope_part', 1)

        # softness attribute
        softness = self.part_properties('softness').get(base_part)
        if softness:
            self.geo.addAttrib(hou.attribType.Vertex, 'softness', 0.0)
            self.set_vertex_attribute('softness', float(softness))

        # roughness attribute
        roughness = self.part_properties('roughness').get(base_part)
        if roughness:
            self.geo.addAttrib(hou.attribType.Vertex, 'roughness', 0.0)
            self.set_vertex_attribute('roughness', float(roughness))

        # graininess attribute
        graininess = self.part_properties('graininess').get(base_part)
        if graininess:
            self.geo.addAttrib(hou.attribType.Vertex, 'graininess', 0.0)
            vertex_list = self.convert_houdini_list(graininess[1])
            self.set_vertex_attribute('graininess', float(graininess[0]), vertex_list)

        # injection point attribute
        injection_point = self.part_properties('injection_point').get(base_part)
        if injection_point:            
            self.geo.addArrayAttrib(hou.attribType.Global, 'injection_point', hou.attribData.String)
            self.geo.setGlobalAttribValue('injection_point', injection_point)