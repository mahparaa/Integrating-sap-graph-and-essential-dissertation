from django.shortcuts import render, redirect
from dotenv import load_dotenv
import os
from django.http import HttpResponse
import time

load_dotenv()

import sys
sys.path.append('..')

from domain import sap_graph as sp_grahp

CLIENT_ID = os.getenv("client.id")
CLIENT_SECRET = os.getenv('client.secret')
REDIRECT_URI = os.getenv('redirect.url')
TOKEN_URL = os.getenv('token.url')

def index(request): 
    return render(request, 'index.djt.html')

def sap_graph(request):
    expires = request.COOKIES.get('expires_in')
    current_time = int(time.time()) + int(expires)
    is_expired = False
    if current_time < int(time.time()):
        is_expired = True
    
    context = {
        'is_expired': is_expired
    }
    
    return render(request, 'sap-graph.djt.html', context)

def essentail_architecture(request):
    return render(request, 'essential-architecture.djt.html')

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

def sap_execute_neo4j_query(request):
    return render(request, 'sap-graph.djt.html')


def sap_sync_all_the_entites(request):
    # TODO get all the entities data
    return render(request)