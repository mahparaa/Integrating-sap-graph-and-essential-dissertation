from gspan_mining.config import parser
from gspan_mining.main import main
from gspan_mining.graph import Graph, Vertex
from pyvis.network import Network
from apyori import apriori
import networkx as nx
from pyvis.network import Network
import matplotlib.pyplot as plt

dir = '../data/gspan/graph.data'
nt = Network()

def apply_gspan(G: Network):
    converted_data = _convert_network_to_string(G)
    with open(dir, "w") as myfile:
        myfile.write(converted_data)

    args_str = '-s 25 -d False -l 10 -p False -w False {0}'.format(dir)
    FLAGS, _ = parser.parse_known_args(args=args_str.split())
    gs = main(FLAGS)

    for i, grp in enumerate(gs.graphs.values()):
        _convert_string_to_network(grp, i)


def apply_association_rule_mining(entities_relationsips: dict,
                                  min_support = 0.0009,
                                  min_confidence = 0.2,
                                  min_lift = 3,
                                  min_length = 2,
                                  cli = True):
    transaction = []
    for node_name_key, entities in entities_relationsips.items():
        parent_node = [ node_name_key, 
                       '' 
        ]
        # attributes = _get_attribute_details(entities)
        # row = { **parent_node, **attributes }

        transaction.append(parent_node)

        for relation in entities['relationships']:
            # TODO use attributes?
            # attribute_name = relation['attribute_name']
            # attribute_type = relation['attribute_type']
            node_name = relation['ref']
            transaction.append([ node_name, 
                               node_name_key 
                               ])
            
    association_rules = apriori(transaction, min_support=min_support, min_confidence=min_confidence, min_lift=min_lift, min_length=min_length)
    association_results = list(association_rules)
    G = Network(directed=True)

    print(len(association_results))
    data = []
    for rule in association_results:
        antecedents = rule.ordered_statistics[0].items_base
        consequents = rule.ordered_statistics[0].items_add
        support = rule.support
        confidence = rule.ordered_statistics[0].confidence

        label_antecendents = list(antecedents)[0]
        label_consequents = list(consequents)[0]
        G.add_node(label_antecendents)
        G.add_node(label_consequents)
        G.add_edge(label_antecendents, label_consequents)
        # Create Data Objects with entity names
        data_object = {
            'antecedents': label_antecendents,
            'consequents': label_consequents,
            'support': support,
            'confidence': confidence
        }
        # print(data_object)
        data.append(data_object)
    
    if cli:
        G.save_graph('ar-mining.html')
    return (G, data)
    

def _get_attribute_details(data: dict) -> dict:
    new_dict = {}
    for key, value in data.items():
        if key == 'relationships':
            continue
        for k, v in value.items():
            new_dict[k] = v
    return new_dict


def _convert_string_to_network(grp: Graph, i: int) -> Network:
    vertices = grp.vertices
    for vertice in vertices:
        v_graph: Vertex = vertices[vertice]
        nt.add_node(vertice)
        edges = v_graph.edges
        for edge in edges:
            nt.add_node(edge)
            nt.add_edge(vertice, edge)
    print('[END] _convert_string_to_network')
    nt.save_graph('mined/test-{0}.html'.format(i))

def _convert_network_to_string(network: Network):
    output = "t # 0\n"

    nodes = network.nodes
    node_inc = 1
    edge_inc = 1
    t_inc = 1
    for node in nodes:
        node_id = node['id']
        output += "v {0} {1}\n".format(node_id, node_inc)
        neigbhours = network.neighbors(node_id)
        for neigbhour in neigbhours:
            node_inc += 1
            output += "v {0} {1}\n".format(neigbhour, node_inc)
        for neigbhour in neigbhours:
            edge_inc += 1
            output += "e {0} {1} {2}\n".format(node_id, neigbhour, edge_inc)
            
        output += 't # {0}\n'.format(t_inc)
        t_inc += 1
        node_inc = 1
        edge_inc = 1
        
    output += 't # -1'
    return output