from gspan_mining.config import parser
from gspan_mining.main import main
from gspan_mining.graph import Graph, Vertex
from pyvis.network import Network


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