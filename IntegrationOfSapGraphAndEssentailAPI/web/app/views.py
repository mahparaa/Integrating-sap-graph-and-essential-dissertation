from django.shortcuts import render, redirect
from dotenv import load_dotenv
import os
from django.http import HttpResponse
from django.http import JsonResponse
import time
import json
from django.contrib.sessions.backends.db import SessionStore

load_dotenv()

import sys
sys.path.append('..')

from domain import sap_graph as sp_grahp
from domain import connect_neo4j as c_neo4j
from domain import essential_api as ea

CLIENT_ID = os.getenv("client.id")
CLIENT_SECRET = os.getenv('client.secret')
REDIRECT_URI = os.getenv('redirect.url')
TOKEN_URL = os.getenv('token.url')
GRAPH_URL = os.getenv('graph.url')
GRAPH_ID = os.getenv('graph.id')
APP_INT_ID = os.getenv('application.interface.key')

sap_dir = '../data/sap/'

def index(request): 
    return render(request, 'index.djt.html')

def sap_graph(request):
    expires = request.COOKIES.get('expires_in')
    expires = expires if expires else 0
    
    current_time = int(time.time()) + int(expires)
    is_expired = False
    if current_time < int(time.time()) or expires == 0:
        is_expired = True
    
    context = {
        'is_expired': is_expired,
        'total_synced': len([name for name in os.listdir(sap_dir)])
    }
    
    return render(request, 'sap-graph.djt.html', context)

def login_to_ea(request):
    del request.session

    response = HttpResponse("Session deleted")
    response.delete_cookie('sessionid')

    return render(request, 'ea-login.djt.html')

def handle_login_to_ea(request):
    api_key = request.POST.get('apiKey')
    password = request.POST.get('password')
    username = request.POST.get('username')
    
    login = ea.LoginApi(cli=False)
    login.login_get_oauth_token(username, password, api_key)
    token_details = login.get_token()
    
    session = SessionStore()
    session['bearer_token'] = token_details['access_token']
    session['refresh_token'] = token_details['refresh_token']
    set_expiry = token_details['expires_in_minutes'] * 60 * 1000
    session.set_expiry(set_expiry)

    session.save()
    response = HttpResponse("Session set successfully")
    response.set_cookie('sessionid', session.session_key, expires=set_expiry)

    response['Location'] = '/essential-architecture'
    response.status_code = 302

    return response

def essentail_architecture(request):
    session = request.session
    has_session = False
    
    if not session.get('bearer_token') == None:
        has_session = True
    context = { "has_session": has_session }
    return render(request, 'essential-architecture.djt.html', context = context)

def login_sap(request):
    url = '{0}/oauth/authorize?client_id={1}&redirect_uri={2}&response_type=code'.format(TOKEN_URL, CLIENT_ID, REDIRECT_URI)
    return redirect(url)

def sap_login_callback(request):
    headers = { 
        'Content-Type': 'application/x-www-form-urlencoded', 
        'Accept': 'application/json'
    }
    params = {
        'code': request.GET.get('code'),
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
    }
    
    url = '{0}/oauth/token'.format(TOKEN_URL)
    result = sp_grahp.call_login_api(url, params, headers)
    response = HttpResponse('Response')
    response.set_cookie('access_token', result['access_token'])
    response.set_cookie('refresh_token', result['refresh_token'])
    response.set_cookie('expires_in', result['expires_in'])
    response['Location'] = '/sap-graph'
    response.status_code = 302

    return response

def sap_logout_remove_cookies(request):
   
    response = HttpResponse('Response')
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    response.delete_cookie('expires_in')
    response['Location'] = '/sap-graph'
    response.status_code = 302

    return response

def sap_execute_neo4j_query(request):
    #TODO execute query and map to network
    return render(request, 'sap-graph.djt.html')

def sync_to_neo4j(request):
    json_files = [pos_json for pos_json in os.listdir(sap_dir) if pos_json.endswith('.json')]
    for json_file in json_files:
        with open(sap_dir + json_file, 'r') as f:
            sp_grahp.get_all_component(json.loads(f.read()))

    network = sp_grahp.create_graph(sp_grahp.relationship_with_entity)
    c_neo4j.create_data(network)

    return JsonResponse({ 'success': True })

def search_from_neo4j(request):
    from_ = request.GET.get('from_entity')
    data = c_neo4j.get_search_result(from_)
    return JsonResponse(data)

def sap_sync_all_the_entites(request):
    access_token = request.COOKIES.get('access_token')
    data = sp_grahp.download_all_system_entities(GRAPH_URL, GRAPH_ID, access_token, APP_INT_ID)
    return JsonResponse({ 'success': True })


def load_sap_graph_nodes_and_edges(request):
    json_files = [pos_json for pos_json in os.listdir(sap_dir) if pos_json.endswith('.json')]
    for json_file in json_files:
        with open(sap_dir + json_file, 'r') as f:
            sp_grahp.get_all_component(json.loads(f.read()))

    network = sp_grahp.create_graph(sp_grahp.relationship_with_entity)
    return JsonResponse({ 'edges': network.edges, 'nodes': network.nodes  })



def create_information_concepts(request):
    access_token = request.session.get('bearer_token')
    info = ea.InformationConcept(access_token)
    request_data = { 
        "name": "SAP Graph Information Concept",
        "className": "Information_Concept"
    }
    response = info.upload_data(request_data)
    if response.status_code != 200:
        return JsonResponse({ "success": False, "data": response.json() })
    
    return JsonResponse( { "success": True, "data": response.json() })