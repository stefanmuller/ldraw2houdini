import ldraw
import json
import hou
import re

class ldrawPartProperties:
    def __init__(self, node, parms):
        # python sop
        self.node = node
        # store this geo
        self.geo = self.node.geometry()

        self.parm_part = parms.get('parm_part')

    def part_properties(self, property):
        properties = ldraw.resources() / 'part_properties.json'
        with open(properties) as f:
            data = json.load(f)
        property = data[property]

        return property

    def set_vertex_attribute(self, attribute, value, prim_list=[]):
        prims = self.geo.prims()
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
        base_part = self.parm_part
        base_part = re.sub('[a-zA-Z].*', '', base_part) # remove variant string
        base_part = re.sub('\d+-', '', base_part) # remove model string from unofficial mpd part files

        # slope attribute
        if base_part in self.part_properties('slopes'):
            self.geo.addAttrib(hou.attribType.Global, 'slope_part', 1)

        # softness attribute
        softness = self.part_properties('softness').get(base_part)
        if softness:
            self.geo.addAttrib(hou.attribType.Vertex, 'softness', float(softness))

        # roughness attribute
        roughness = self.part_properties('roughness').get(base_part)
        if roughness:
            self.geo.addAttrib(hou.attribType.Vertex, 'roughness', float(roughness))

        # graininess attribute
        graininess = self.part_properties('graininess').get(base_part)
        if graininess:
            if graininess[1] != '':            
                self.geo.addAttrib(hou.attribType.Vertex, 'graininess', 0.0)
                vertex_list = self.convert_houdini_list(graininess[1])
                self.set_vertex_attribute('graininess', float(graininess[0]), vertex_list)
            else:
                self.geo.addAttrib(hou.attribType.Vertex, 'graininess', float(graininess[0]))

        # injection point attribute
        injection_point = self.part_properties('injection_point').get(base_part)
        if injection_point:            
            self.geo.addArrayAttrib(hou.attribType.Global, 'injection_point', hou.attribData.String)
            self.geo.setGlobalAttribValue('injection_point', injection_point)