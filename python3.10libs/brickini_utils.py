import hou

def find_hdas(filter_string):
    '''Return a list of hda files loaded into this Houdini session.'''
    # Look through all the node types, and for those that have digital
    # asset definitions, remember the hda file containing the definition.
    result = []
    for category in hou.nodeTypeCategories().values():
        for node_type in category.nodeTypes().values():
            definition = node_type.definition()
            if definition is None:
                continue
            if definition.libraryFilePath() == 'Embedded':
                continue
            if filter_string not in definition.nodeTypeName():
                continue
            if definition.nodeTypeName() not in result:
                result.append(definition)
    return result

def highest_version(hdas):
    ''' Create a dict that contains only the highest version number '''
    hda_dict = {}
    for item in hdas:
        item_parts = item.nodeType().nameComponents()
        item_type = item_parts[2]
        item_version = item_parts[3]

        if item_type not in hda_dict or item_version > hda_dict[item_type].nodeType().nameComponents()[3]:
            hda_dict[item_type] = item
    return hda_dict

def update_hdas(hda_dict, filter_string):
    ''' Update all hdas to the latest definition'''  
    for nodes in hou.node("/obj").children():
        for n in nodes.children():
            node_type = n.type().nameComponents()[2]
            if filter_string in node_type:
                if node_type in hda_dict:
                    matched_item = hda_dict[node_type].nodeTypeName()
                    n.changeNodeType(matched_item, keep_network_contents=False)

def upgrade_brickini_hdas():
    filter_string = 'brickini'
    hdas = find_hdas(filter_string)
    hda_dict = highest_version(hdas)
    update_hdas(hda_dict, filter_string)


def reload_brickini_nodes():
    '''
    Evals and sets (same) value on specific parms to trigger a reload.
    This can be helpful if you modified an ldraw file or the brick_properties.json or ld_colors.json and want to see its effect.
    '''
    nodes = hou.selectedNodes()
    nodelist = list(nodes)
    for n in nodelist:        
        node_type = n.type().nameComponents()[2]
        if node_type == 'geo':
            nodelist.remove(n)
            nodelist.extend(n.children())

    for n in nodelist:
        node_type = n.type().nameComponents()[2]       
        if node_type == 'brickini_ldraw_part':
            part_parm = n.parm('part')
            part_number = part_parm.eval()
            part_parm.set(part_number)
            # print('reloading {}'.format(n))

        elif node_type == 'brickini_material':
            mat_parms = []
            all_parms = n.parms()

            for a in all_parms:
                if 'material_' in a.name():
                    mat_parms.append(a)
            
            material_group = mat_parms[0].eval()
            material_parm = mat_parms[material_group+1]
            material = material_parm.eval()
            material_parm.set(material)
            # print('reloading {}'.format(n))

        elif node_type == 'brickini_ldraw_model':
            part_parm = n.parm('reload')
            part_parm.pressButton()
            # print('reloading {}'.format(n))