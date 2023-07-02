from pyvis.network import Network
from neo4j import GraphDatabase
import os
from dotenv import load_dotenv

load_dotenv()

NEO_USERNAME = os.getenv('NEO_USERNAME')
NEO_PASSWORD = os.getenv('NEO_PASSWORD')
NEO_URI = os.getenv('NEO_URI')
NEO_ENABLE = os.getenv('NEO_ENABLE')

driver = GraphDatabase.driver(NEO_URI, auth=(NEO_USERNAME, NEO_PASSWORD))

def get_data(label: str):
    splitted = label.split('.')

    domain, module, entity = '', '', ''
    if len(splitted) == 3:
        domain, module, entity = splitted
    else:
        domain_module, entity = label.split('/')
        domain, module = domain_module.split('.')

    return domain, module, entity

def create_node(tx, label):
    domain, module, entity = get_data(label)
    print('Creating Node {0}'.format(entity))
    query = "CREATE (n:{0} {{ domain: '{1}', title: '{2}', name: '{3}' }})".format(entity, domain, module, entity)
    tx.run(query, label=label)


def create_relationship(tx, start_node_id, end_node_id, rel_type):
    s_domain, s_module, s_entity = get_data(start_node_id)
    t_domain, t_module, t_entity = get_data(end_node_id)

    print('Creating Relationship {0} -> {1}'.format(s_entity, t_entity))
    query = """MATCH (a:{0}),(b:{1})
        WHERE a.name = '{0}' AND b.name = '{1}'
        CREATE (a)-[r:CONNECTED_WITH]->(b)
        RETURN r""".format(s_entity, t_entity)
    
    tx.run(query, rel_type=rel_type, start_node_id=start_node_id, end_node_id=end_node_id)

def create_data(G: Network):
    if not NEO_ENABLE == 'True':
        print('Skipping Neo4j syncing and creating database')
        return
    
    with driver.session() as session:
        for attributes in G.nodes:
            label = attributes['label']
            session.write_transaction(create_node, label)
        for edge in G.edges:
            start_node = edge['from']
            end_node = edge['to']
            session.write_transaction(create_relationship, start_node, end_node, 'DIRECTED_IN')

    # Close the database connection
    driver.close()
