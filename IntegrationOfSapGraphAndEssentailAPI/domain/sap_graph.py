from pyvis.network import Network
import requests

def get_name(input_string: str):
    link_format = 'https://eu10.graph.sap/catalog/my-bdg/'
    new_string = input_string.replace(link_format, '')
    splitted_string = new_string.split('#')[0]
    if splitted_string == '':
        return None
    return splitted_string

relationship_with_entity = {}
def fetch_references(title, properties):
    new_list_of_references = []

    for property in properties:
        property_insight = properties[property]
        
        if 'allOf' in property_insight:
            list_of_references = property_insight['allOf']
            for reference in list_of_references:
                ref = reference['$ref']
                ref = get_name(ref)
                if ref is None:
                    continue

                new_list_of_references.append(ref)
        
        if 'items' in property_insight:
            reference = property_insight['items']
            if '$ref' in reference and isinstance(reference, dict):
                ref = reference['$ref']
                ref = get_name(ref)
                if ref is None:
                    continue
                new_list_of_references.append(ref)
            elif isinstance(reference, list):
                for referen in reference:
                    if '$ref' in referen:
                        ref = reference['$ref']
                        ref = get_name(ref)
                        if ref is None:
                            continue
                    new_list_of_references.append(ref)

    if not title in relationship_with_entity:
        relationship_with_entity[title] = new_list_of_references
    else:
        previous_references = relationship_with_entity[title]
        new_list_of_references.extend(previous_references)
        relationship_with_entity[title] = new_list_of_references

    return relationship_with_entity

def get_all_component(schema):
    schemas = schema['components']['schemas']
    title = list(schemas.keys())[0]
    for _, entities in schemas.items():
        if 'properties' not in entities:
            continue

        property = entities['properties']
        fetch_references(title, property)

def get_split_for_group(input_str: str):
    splitting = input_str.split('.')
    sap = splitting[0]
    module = splitting[1].split('/')[0]
    return sap + '.' + module

def create_graph(d: dict, html_file):
    nt = Network()
    nt.layout_algorithm = 'hierarchical'
    nt.force_atlas_2based()

    val_map = {
        'sap.c4c': 'red',
        'sap.s4': 'darkblue',
        'sap.graph': 'green',
    }

    val_shap = {
        'sap.c4c': 'dot',
        'sap.s4': 'star',
        'sap.graph': 'triangle',
    }

    for source, targets in d.items():
        for target in targets:
            s_group = get_split_for_group(target)
            color = val_map.get(s_group, 'black')
            shape = val_shap.get(s_group, 'diamond')
            nt.add_node(source, color=color, label = source, shape=shape, font={'size': 20, 'bold': True} )
            nt.add_node(target, color=color, label = target, shape=shape, font={'size': 20, 'bold': True})
            nt.add_edge(source, target, color=color, width=3)

    nt.save_graph(html_file)
    return nt


def call_login_api(url: str, body: dict, headers: dict):
    response = requests.request('POST', url, data=body, headers=headers)
    if response.status_code != 200:
        raise Exception('Logging to SAP fails', response.json())
    
    data = response.json()
    return data