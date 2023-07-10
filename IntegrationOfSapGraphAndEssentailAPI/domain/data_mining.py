from gspan_mining.config import parser
from gspan_mining.main import main
from pyvis.network import Network
import networkx

dir = '../data/gspan/graph.data'

def apply_gspan(G: Network):
    converted_data = _convert_network_to_string(G)
    with open(dir, "w") as myfile:
        myfile.write(converted_data)

    args_str = '-s 2 -d True -l 5 -p True -w True {0}'.format(dir)
    FLAGS, _ = parser.parse_known_args(args=args_str.split())
    gs = main(FLAGS)

    print(gs.graphs.__len__())
    # for g in gs.graphs.values():
    #     print(gg)

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
    # t_inc = 0
    # history = []
    # node_mapping = {}
    # for i, node_id in enumerate(network.nodes):
    #     # if not node_id['id'] in history:
    #     node_mapping[node_id['id']] = i
    #     # history.append(history)

    # edge_mapping = {}
    # for i, edge_data in enumerate(network.edges):
    #     edge_mapping[edge_data['from'] + edge_data['to']] = i

    # t_inc = 0
    # for node_id, node_index in node_mapping.items():
    #     # if not node_id in history:
    #     output += f"v {node_id} {node_index}\n"
    #     # else:
    #     #     t_inc += 1
    #     output += 't # {0}'.format(t_inc)
    #     history.append(node_id)


    # # Convert edges to format
    # for edge_data in network.edges:
    #     # from_index = node_mapping[edge_data['from']]
    #     # to_index = node_mapping[edge_data['to']]
    #     # edge_index = edge_mapping[edge_data['from'] + edge_data['to']]
    #     from_index = edge_data['from']
    #     to_index = edge_data['to']
    #     edge_index = edge_mapping[edge_data['from'] + edge_data['to']]
    #     output += f"e {from_index} {to_index} {edge_index}\n"

    output += 't # -1'
    return output