# pyright: reportMissingImports=false
from pathlib import Path, PureWindowsPath
import ldraw
import hou
import re
import importlib

importlib.reload(ldraw)

class ldrawPart:
    def __init__(self, node, parms):
        self.ldraw_lib = ldraw.ldraw_lib()
        self.color_dict = ldraw.color_lib()
        self.material_groups = ldraw.material_group()
        self.default_color = hou.Vector3(1, 1, 1)

        # python sop
        self.node = node

        # store all the parms
        self.parm_part = parms.get('parm_part')
        self.parm_highres = parms.get('parm_highres')
        self.parm_logo = parms.get('parm_logo')
        self.parm_stud = parms.get('parm_stud')
        self.parm_pack = parms.get('parm_pack')
        self.parm_print = parms.get('parm_print')
        self.parm_edges = parms.get('parm_edges')
        self.parm_material_group = parms.get('parm_material_group')
        self.parm_material = parms.get('parm_material')

        # store this geo
        self.geo = self.node.geometry()

        # attr names
        self.col_attr = 'Cd'
        self.mat_attr = 'material_type'

        if self.parm_pack:
            self.col_attr = self.col_attr + '2'
            self.mat_attr = self.mat_attr + '2'

        # write attributes
        self.geo.addArrayAttrib(hou.attribType.Global, 'part_color', hou.attribData.Float)
        self.geo.setGlobalAttribValue('part_color', self.color_dict[str(self.parm_material)]['rgb'])

        self.geo.addAttrib(hou.attribType.Global, 'name', '')
        self.geo.setGlobalAttribValue('name', 'p_' + self.parm_part)

        self.geo.addAttrib(hou.attribType.Global, 'description', '')

        self.texture_path = self.ldraw_lib / 'textures' / str(self.parm_part + '_basecolor.png')

        if self.parm_print == 2:
            self.geo.addAttrib(hou.attribType.Global, 'print', '')
            self.geo.setGlobalAttribValue('print', str(self.texture_path))

        self.subpart_cache = {}

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

    def create_lines(self, points, line_geo):
        '''create lines from points'''
        poly = line_geo.createPolygon()
        for position in points:
            point = line_geo.createPoint()
            point.setPosition(position)
            poly.addVertex(point)
            poly.setIsClosed(False)

        return line_geo

    def create_polys(self, polys_data, part_geo):
        '''
        Batch create polygons and set attributes in bulk.
        polys_data: list of dicts with keys: points, color, static_color, color_code, info, mat_type
        '''
        # Collect all data
        all_points = []
        polygons_indices = []
        color_codes = []
        infos = []
        colors = []
        mat_types = []
        color_modes = []

        for poly in polys_data:
            start_idx = len(all_points)
            all_points.extend(poly['points'])
            polygons_indices.append(tuple(range(start_idx, start_idx + len(poly['points'])))
            )
            color_codes.append(int(poly['color_code']))
            infos.append(poly['info'])
            if not self.parm_pack:
                colors.append(poly['color'])
                mat_types.append(poly['mat_type'])
            else:
                colors.append(poly['color'])
                mat_types.append(poly['mat_type'])
                color_modes.append(1 if poly['static_color'] else 0)

        # Create all points
        point_objs = part_geo.createPoints(all_points)

        # Create polygons using tuples of point objects
        polygons = []
        for poly_indices in polygons_indices:
            polygons.append(tuple(point_objs[idx] for idx in poly_indices))
        part_geo.createPolygons(polygons)

        # Flatten colors
        flat_colors = [f for c in colors for f in c]

        # Set attributes in bulk
        part_geo.setPrimIntAttribValues('color_code', color_codes)
        part_geo.setPrimStringAttribValues('info', infos)
        part_geo.setPrimFloatAttribValues(self.col_attr, flat_colors)
        part_geo.setPrimIntAttribValues(self.mat_attr, mat_types)
        
        if  self.parm_pack:
            part_geo.setPrimIntAttribValues('color_mode', color_modes)

        return part_geo

    def determine_winding(self, winding_group, m4, invert_next):
        '''
        this function determines winding order
        invert winding again if orientation matrix is reversed (negative determinant)
        cancel out inversion if INVERTNEXT statement is found before subpart reference
        '''
        m4_det = m4.determinant()
        if m4_det < 0:
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
    
    def get_color(self, color_code):
        '''
        get color from ld color json
        16 is a special code, the color is determined by the referenced dat file
        '''
        static_color = True
        mat_type = self.parm_material_group
        color = hou.Vector3(1, 0, 0.5)

        if color_code == '16':
            color = self.color_dict[str(self.parm_material)]['rgb']
            static_color = False
        else:
            # if x in color it's a direct color that looks like this: 0x2995220
            # and we need to convert it manually
            if 'x' in color_code:
                color = ldraw.hex_to_acescg(color_code[3:9])
                color_code = '0'
            else:
                try:
                    color = self.color_dict[color_code]['rgb']
                    mat_type = self.material_groups.index(self.color_dict[color_code]['category'])
                except:
                    pass

        return color, static_color, color_code, mat_type

    def path_resolve(self, part):
        '''
        Efficiently find part in ldraw lib.
        '''
        # Normalize part name
        part = str(PureWindowsPath(part)).replace(' ', '')
        part_lower = part.lower()

        # Try both original and lowercase
        part_names = [part, part_lower]

        # List of (directory, highres_directory) tuples to search
        search_paths = [
            (ldraw.p, None),
            (ldraw.ps, None),
            (ldraw.pr, ldraw.pr48),
            (ldraw.p_u, None),
            (ldraw.ps_u, None),
            (ldraw.pr_u, ldraw.pr48_u),
            (ldraw.pr_l2h, None),
        ]

        for name in part_names:
            for base_dir, highres_dir in search_paths:
                part_dir = base_dir / name
                if part_dir.exists():
                    # Check for highres override if requested
                    if self.parm_highres and highres_dir is not None:
                        highres_part = highres_dir / name
                        if highres_part.exists():
                            return highres_part
                    return part_dir

        # Fallback if not found
        return ldraw.pr_l2h / 'box-part-not-found.dat'

    def read_part(self, part, winding, color_code, info, stud_processing):
        '''
        recursive function that reads the part and then either creates
        lines, tris, quads or reads subparts inside the part
        subparts are stored in a dict and then reused for all remaining instances
        '''
        if not part.exists():
            return

        with open(part) as f:
            invert_next = False
            winding_sub = winding
            info_group = info
            color_group = color_code
            static_color = False

            part_geo = hou.Geometry()
            temp_geo = hou.Geometry()
            temp_geo2 = hou.Geometry()
            line_geo = hou.Geometry()

            if self.parm_pack:
                part_geo.addAttrib(hou.attribType.Prim, 'color_mode', 0)

            part_geo.addAttrib(hou.attribType.Prim, self.col_attr, self.default_color)
            part_geo.addAttrib(hou.attribType.Prim, self.mat_attr, self.parm_material_group)
            part_geo.addAttrib(hou.attribType.Prim, 'info', '')
            part_geo.addAttrib(hou.attribType.Prim, 'color_code', 0)

            # write description from first line if it matches the part number
            if self.parm_part == part.stem:
                description = f.readline().split(' ', 1)[-1].replace(' ', '_').strip()
                self.geo.setGlobalAttribValue('description', description)

            # Collect polygon data for batch creation
            polys_data = []

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

                    # inverse winding order until end of file or until next such statement found
                    elif line[1] == 'BFC' and line[2] == 'CW':
                        winding_sub = 'CW'
                    elif line[1] == 'BFC' and line[2] == 'CCW':
                        winding_sub = 'CCW'

                    # subpart that we'll find in the line after this one needs to be inversed
                    elif line[1] == 'BFC' and line[2] == 'INVERTNEXT':
                        invert_next = True

                    # check for deactivated logo line, swap to logo4.dat (best looking one) and activate the line
                    if self.parm_logo == 1:
                        if 'logo' in line[-1]:
                            line = line[2:]
                            line[-1] = 'logo4.dat'

                # part/prim reference
                if line[0] == '1':
                    part = ' '.join(line[14:])

                    # if separate mode we don't process studs from base part, but only from the printed one
                    if stud_processing == 0 and 'stu' in part:
                        continue

                    # load special stud-instance which is just a helper prim to be able to instance the actual stud geo in the hda network
                    if self.parm_stud:
                        if part == 'stud.dat':
                            part = 'stud-instance.dat'
                            info_group = 'stud-instance'
                        elif part == 'stud2.dat':
                            part = 'stud-instance.dat'
                            info_group = 'stud2-instance'
                        elif 'stu' in part:
                            info_group = 'stud'
                        else:
                            info_group = info

                    if 'logo' in part:
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
  
                    m4 = ldraw.get_matrix(line)

                    winding_group = self.determine_winding(winding_group, m4, invert_next)
                    invert_next = False

                    # Adding the winding_group to the part name means we are potentially storing 2 versions of any given subpart.
                    # This feels somewhat dumb, but since there is no 'flip vertex order function', there isn't really any smarter alternative I can think of.
                    part_name = '{}_{}'.format(part, winding_group)

                    # check if subpart was already built and store in temp_geo
                    if part_name in self.subpart_cache:
                        if info_group != 'print' or (info_group == 'print' and (color_code != '16' or 16 not in self.subpart_cache[part_name].primIntAttribValues('color_code'))): # make sure in separate mode that studs are processed correctly
                            temp_geo.copyPrims(self.subpart_cache[part_name])
                        else:
                            continue
                    else:
                        part = self.path_resolve(part)
                        
                        part_geo_group = self.read_part(part, winding_group, color_code, info_group, stud_processing)
                        #store subpart
                        if len(part_geo_group.prims()) > 0:
                            self.subpart_cache[part_name]=part_geo_group                        
                        temp_geo.copyPrims(part_geo_group)

                    color, static_color, color_code, mat_type = self.get_color(line[1])
                    
                    # the following sets the correct attributes based on parent parts/subparts
                    # it's waaay faster to use primXAttribValues on the geo rather than looping over the prims and setting values directly
                    color_codes = temp_geo.primIntAttribValues('color_code')
                    colors = temp_geo.primFloatAttribValues(self.col_attr)
                    mat_types = temp_geo.primIntAttribValues(self.mat_attr)
                    infos = temp_geo.primStringAttribValues('info')

                    new_color_codes = list(color_codes)
                    new_colors = list(colors)
                    new_mat_types = list(mat_types)
                    new_infos = list(infos)
                    new_color_modes = list()

                    if self.parm_pack:
                        color_modes = temp_geo.primIntAttribValues('color_mode')
                        new_color_modes = list(color_modes)

                    for i, code in enumerate(color_codes):
                        if code == 16:
                            s = i * 3
                            new_colors[s:s+3] = color
                            new_color_codes[i] = int(color_code)
                            new_mat_types[i] = mat_type
                            if infos[i] == '':
                                new_infos[i] = info_group
                            if static_color and self.parm_pack:
                                new_color_modes[i] = 1

                    # Write back in bulk
                    temp_geo.setPrimFloatAttribValues(self.col_attr, new_colors)
                    temp_geo.setPrimIntAttribValues('color_code', new_color_codes)
                    temp_geo.setPrimIntAttribValues(self.mat_attr, new_mat_types)
                    temp_geo.setPrimStringAttribValues('info', new_infos)
                    if self.parm_pack:
                        temp_geo.setPrimIntAttribValues('color_mode', new_color_modes)

                    temp_geo.transform(m4)                    
                    temp_geo2.mergePrims(temp_geo)

                # tri
                elif line[0] == '3':
                    color, static_color, color_code, mat_type = self.get_color(line[1])
                    points = self.extract_points(line, 3, winding_sub)
                    if info != 'print' or (info == 'print' and (color_code != '16' or color_group != '16')): # make sure in separate mode that studs are processed correctly
                        polys_data.append({
                            'points': points,
                            'color': color,
                            'static_color': static_color,
                            'color_code': color_code,
                            'info': info,
                            'mat_type': mat_type
                        })

                # quad
                elif line[0] == '4':
                    color, static_color, color_code, mat_type = self.get_color(line[1])
                    points = self.extract_points(line, 4, winding_sub)
                    if info != 'print' or (info == 'print' and (color_code != '16' or color_group != '16')): # make sure in separate mode that studs are processed correctly
                        polys_data.append({
                            'points': points,
                            'color': color,
                            'static_color': static_color,
                            'color_code': color_code,
                            'info': info,
                            'mat_type': mat_type
                        })

                # lines
                if self.parm_edges and info == 'base':
                    if line[0] == '2':
                        color = [0,0,0]
                        static_color = False
                        points = self.extract_points(line, 2, winding_sub)
                        line_geo = self.create_lines(points, line_geo)

            # Batch create polygons and set attributes
            if polys_data:
                part_geo = self.create_polys(polys_data, part_geo)

            part_geo.mergePrims(temp_geo2)
            part_geo.mergePrims(line_geo)
        return part_geo

    def __call__(self):
        # print handling
        # load brick as set in parm parameter by default
        # load base brick if mode is set to separate and only keep print geo from actual brick
        # load base brick if mode is set to texture and we create uvs in the hda

        m4_ldu = ldraw.xform_to_houdini()

        base_part = self.parm_part
        print_str = re.search('[pP].*', self.parm_part)
        composite_str = re.search('[cC].*', self.parm_part)
        stud_processing = 1

        if print_str != None:
            print_str = print_str.group()
            base_part = self.parm_part.replace(print_str, '')
            base_part = re.sub(r'\d+-', '', base_part) # remove model string from unofficial mpd part files

        # if part is a composite we won't apply separation since base composite part might not exist
        if self.parm_print > 0 and print_str != None and composite_str == None:
            if self.parm_print == 1:
                part_path = self.path_resolve(self.parm_part + '.dat')
                part_geo_print = self.read_part(part_path, 'CCW', '16', 'print', 1)
                stud_processing = 0
                part_geo_print.transform(m4_ldu)
                self.geo.mergePrims(part_geo_print)
                # clear subpart cache so printed areas don't conflict with non printed ones
                self.subpart_cache.clear()

            self.parm_part = base_part

        part_path = self.path_resolve(self.parm_part + '.dat')
        part_geo_base = self.read_part(part_path, 'CCW', '16', 'base', stud_processing)
    
        # transform and add to main geo object
        part_geo_base.transform(m4_ldu)
        self.geo.mergePrims(part_geo_base)