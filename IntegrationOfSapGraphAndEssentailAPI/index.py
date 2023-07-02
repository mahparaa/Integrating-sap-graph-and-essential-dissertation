import os
import json
import logging
import essential_api
import sap_graph
import connect_neo4j

logging.basicConfig(level = logging.INFO)


if __name__ == '__main__':
    logging.info('Creating graph visualization')
    json_files = [pos_json for pos_json in os.listdir('./data/sap/') if pos_json.endswith('.json')]
    for json_file in json_files:
        with open('./data/sap/' + json_file, 'r') as f:
            sap_graph.get_all_component(json.loads(f.read()))

    html_file = 'network_graph.html'
    logging.info("Graph created to visualize open " + html_file + " in browser")

    graph = sap_graph.create_graph(sap_graph.relationship_with_entity, html_file)
    connect_neo4j.create_data(graph)
    
    # busCap = essential_api.BusinessCapabilityApi()
    
    logging.info('Loading .json files')
    json_files = [pos_json for pos_json in os.listdir('./data/sap/') if pos_json.endswith('.json')]

    logging.info('Creating graph visualization')
    for json_file in json_files:
        with open('./data/' + json_file, 'r') as f:
            sap_graph.get_all_component(json.loads(f.read()))
    html_file = "network_graph.html"
    logging.info("Graph created to visualize open " + html_file + " in browser")
    sap_graph.create_graph(sap_graph.relationship_with_entity, html_file)

    login = essential_api.LoginApi()
    if not 'access_token' in login.get_token():
        login.login_get_oauth_token()
        logging.info('Token Created!')
    
    ## TODO use the graph/network data for Essential API.
    ## TODO use other Essential API.
    business = essential_api.BusinessCapabilityApi(login)
    business.upload_data({})
