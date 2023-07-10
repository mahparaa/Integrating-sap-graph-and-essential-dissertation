import os
import json
import logging

import sys
sys.path.append('..')

import domain.essential_api as essential_api
import domain.sap_graph as sap_graph 
import domain.connect_neo4j as connect_neo4j
import domain.data_mining as dm

logging.basicConfig(level = logging.INFO)

sap_dir = '../data/sap/'

if __name__ == '__main__':
    logging.info('Creating graph visualization')
    json_files = [pos_json for pos_json in os.listdir(sap_dir) if pos_json.endswith('.json')]
    for json_file in json_files:
        with open(sap_dir + json_file, 'r') as f:
            sap_graph.get_all_component(json.loads(f.read()))

    html_file = 'network_graph.html'
    logging.info("Graph created to visualize open " + html_file + " in browser")

    graph = sap_graph.create_graph(sap_graph.relationship_with_entity, html_file)
    dm.apply_gspan(graph)

    # connect_neo4j.create_data(graph)
    
    # login = essential_api.LoginApi()
    # if not 'access_token' in login.get_token():
    #     login.login_get_oauth_token()
    #     logging.info('Token Created!')
    
    ## TODO use the graph/network data for Essential API.
    ## TODO use other Essential API.
    # business = essential_api.BusinessCapabilityApi(login)
    # business.upload_data({})
