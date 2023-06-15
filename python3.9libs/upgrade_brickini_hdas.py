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

def main():
    filter_string = 'brickini'
    hdas = find_hdas(filter_string)
    hda_dict = highest_version(hdas)
    update_hdas(hda_dict, filter_string)


