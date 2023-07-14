import os
from dotenv import load_dotenv
import requests
import logging
import json
import pandas as pd
import math
import curlify

logging.basicConfig(level = logging.INFO)


load_dotenv()

EA_API_KEY = os.getenv('EA_API_KEY')
EA_BASE_URL = os.getenv('EA_BASE_URL')
EA_USERNAME = os.getenv('EA_USERNAME')
EA_PASSWORD = os.getenv('EA_PASSWORD')
REPO_ID = os.getenv('REPOSITORY_ID')
SINGLE_INSTANCE_URL = EA_BASE_URL + 'api/essential-utility/v3/repositories/{0}/instances'.format(REPO_ID)
BATCH_INSTANCE_URL = EA_BASE_URL + 'api/essential-utility/v3/repositories/{0}/instances/batch'.format(REPO_ID)

class LoginApi:
    def __init__(self, cli = True):
        self.cli = cli
        if cli:
            self.AUTHORIZATION_TOKEN = self._load_token()
        else:
            self.AUTHORIZATION_TOKEN = {}

    def get_token(self):
        return self.AUTHORIZATION_TOKEN
    
    def store_token(self):
        with open('./token/login.json', 'w') as json_file:
            json.dump(self.AUTHORIZATION_TOKEN, json_file)

    def _load_token(self):
        with open('./token/login.json', 'r') as json_file:
            return json.load(json_file)

    def login_get_oauth_token(self, username = '', password = '', apikey = ''):
        logging.info('Getting access token')

        url = EA_BASE_URL + "api/oauth/token"

        payload = json.dumps({
        "username": EA_USERNAME if self.cli else username,
        "password": EA_PASSWORD if self.cli else password,
        "grantType": "password"
        })
        headers = {
        'Content-Type': 'application/json',
        'x-api-key': EA_API_KEY if self.cli else apikey,
        'Host': 'shuteaching2.essentialintelligence.com',
        }
        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code != 200:
            logging.error(response.text)
            return response
        
        data = response.json()
        self.AUTHORIZATION_TOKEN['access_token'] = data['bearerToken']
        self.AUTHORIZATION_TOKEN['refresh_token'] = data['refreshToken']
        self.AUTHORIZATION_TOKEN['expires_in_minutes'] = data['expiresInMinutes']

        if self.cli:
            self.store_token()

    def refresh_token(self, refresh_token, apikey = ''): 
        body = {
            "grantType": "refresh_token",
            "refreshToken": refresh_token
        }
        

        headers = {
            'Content-Type': 'application/json',
            'x-api-key': EA_API_KEY if self.cli else apikey
        }
        url = EA_BASE_URL + "api/oauth/token"
        response = requests.request("POST", url, headers=headers, data=body)
        if (response.status_code != 200):
            return False
        
        data = response.json()
        self.AUTHORIZATION_TOKEN['access_token'] = data['bearerToken']
        self.AUTHORIZATION_TOKEN['refresh_token'] = data['refreshToken']
        self.AUTHORIZATION_TOKEN['expires_in_minutes'] = data['expiresInMinutes']


class BusinessCapabilityApi:
    def __init__(self, token: str ) -> None:
        self.token = token

    def upload_data(self, data) -> None:
        logging.info('Uploading business capabilities')
        data = self._prepare_dataset(data)
        headers = { 'Content-type': 'application/json', 'Authorization': self.token, 'x-api-key': EA_API_KEY}

        response = requests.request("POST", BATCH_INSTANCE_URL, headers=headers, data=data)

        if response.status_code != 200:
            logging.error(response.text)
            return
        
        data = response.json()


    def _prepare_dataset(self, df: pd.DataFrame) -> dict:
        instances = []
        for index, row in df.iterrows():
            instance_data = {}
            instance_data['name'] = row['Name']
            instance_data['description'] = row['Description'] if row['Description'] == 'nan' else ''
            instance_data['className'] = "Business_Capability"
            if not row['Parent Business Capability'] == 'nan':
                instance_data['supports_business_capabilities'] = [
                    { 
                        "name": row['Parent Business Capability'], 
                        "className": "Business_Capability" 
                    }
                ]

            if not math.isnan(row['Business Domain']):
                instance_data['belongs_to_business_domains'] = [
                    { "name": row['Business Domain'] }
                ]
            instance_data['business_capability_index'] = row['Sequence Number'] if row['Sequence Number'] == 'nan' else ''
            instances.append(instance_data)
        
        return { "instances": instances }
    


class InformationConcept:
    def __init__(self, access_token):
        self.token = access_token
        self.external_ids = [
            {
                "sourceName": "Essential Launchpad",
                "id": "BC56"
            }]
        self.url = SINGLE_INSTANCE_URL
        self.headers = { 
            'Authorization': 'Bearer {0}'.format(access_token),
            'x-api-key': EA_API_KEY,
            'Content-Type': 'application/json'
            }

    def upload_data(self, data: dict):
        return self._create_concept(data)

    def _create_concept(self, data):
        business_domain_name = "SAP Graph Business Domain"
        business_domain_class = "Business_Domain"

        info_domain_name = "SAP Graph Information Domain"
        info_domain_class = "Information_Domain"

        info_view_name = "SAP Graph Information View"
        info_view_class = "Information_View"

        info_objective_name = "SAP Graph Information Concept"
        info_objective_class = "Information_Concept"

        bd_response = self._create_business_domain({ "name" : business_domain_name, "className": business_domain_class})
        if bd_response.status_code != 200:
            return bd_response
        id_response = self._create_information_domain({ "name": info_domain_name, "className": info_domain_class })
        if id_response.status_code != 200:
            return id_response
        civ_response = self._create_information_views({ "name": info_view_name, "className": info_view_class })
        if civ_response.status_code != 200:
            return civ_response
        cio_response = self._create_information_objectives({ "name": info_objective_name, "className": info_objective_class })
        if cio_response.status_code != 200:
            return cio_response
        request_data = {
            "name": data["name"],
            "className": data["className"],
            "description": "This is a automated generation for SAP Graph visualization",
            "belongs_to_business_domain_information": {
                "name": business_domain_name,
                "className": business_domain_class,
                "id": bd_response.json()['id']
            },
            "info_concept_info_domain": {
                "name": info_domain_name,
                "className": info_domain_class,
                "id": id_response.json()['id']
            },
            "has_information_views": [{
                "name": info_view_name,
                "className": info_view_class,
                "id": civ_response.json()['id']
            }],
            "relevant_information_objectives": [{
                "name": info_objective_name,
                "className": info_objective_class,
                "id": cio_response.json()['id'],
            }],
            "externalIds": self.external_ids,
        }
        
        return self._send_post_request(request_data)

    def _create_business_domain(self, data: dict):
        data['externalIds'] = self.external_ids
        return self._send_post_request(data)
    
    def _create_information_domain(self, data: dict):
        data['externalIds'] = self.external_ids
        return self._send_post_request(data)

    def _create_information_views(self, data: dict):
        data['externalIds'] = self.external_ids
        return self._send_post_request(data)

    def _create_information_objectives(self, data: dict):
        data['externalIds'] = self.external_ids
        return self._send_post_request(data)

    def _send_post_request(self, data):
        payload = json.dumps(data)
        response = requests.request('POST', self.url, headers=self.headers, data=payload)
        print(curlify.to_curl(response.request))
        if response.status_code != 200:
            print('Response has an error ' + str(response))

        return response

    def already_exists_send_data(self, data):
        # TODO If already exist just send its details or only id
        pass