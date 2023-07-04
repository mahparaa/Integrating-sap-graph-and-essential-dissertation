import os
from dotenv import load_dotenv
import requests
import logging
import json
import pandas as pd
import math

logging.basicConfig(level = logging.INFO)


load_dotenv()

EA_API_KEY = os.getenv('EA_API_KEY')
EA_BASE_URL = os.getenv('EA_BASE_URL')
EA_USERNAME = os.getenv('EA_USERNAME')
EA_PASSWORD = os.getenv('EA_PASSWORD')
REPO_ID = os.getenv('REPOSITORY_ID')

class LoginApi:
    def __init__(self):
        self.AUTHORIZATION_TOKEN = self._load_token()

    def get_token(self):
        return self.AUTHORIZATION_TOKEN
    
    def store_token(self):
        with open('./token/login.json', 'w') as json_file:
            json.dump(self.AUTHORIZATION_TOKEN, json_file)

    def _load_token(self):
        with open('./token/login.json', 'r') as json_file:
            return json.load(json_file)

    def login_get_oauth_token(self):
        logging.info('Getting access token')

        url = EA_BASE_URL + "api/oauth/token"

        payload = json.dumps({
        "username": EA_USERNAME,
        "password": EA_PASSWORD,
        "grantType": "password"
        })
        headers = {
        'Content-Type': 'application/json',
        'x-api-key': EA_API_KEY
        }
        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code != 200:
            logging.error(response.text)
            return
        
        data = response.json()
        self.AUTHORIZATION_TOKEN['access_token'] = data['bearerToken']
        self.AUTHORIZATION_TOKEN['refresh_token'] = data['bearerToken']

        self.store_token()

class BusinessCapabilityApi:
    def __init__(self, login: LoginApi) -> None:
        self.token = login.get_token()['access_token']

    def upload_data(self, data) -> None:
        logging.info('Uploading business capabilities')
        data = self._prepare_dataset(data)
        
        url = EA_BASE_URL + 'api/essential-utility/v3/repositories/{0}/instances/batch'.format(REPO_ID)
        headers = { 'Content-type': 'application/json', 'Authorization': self.token, 'x-api-key': EA_API_KEY}

        response = requests.request("POST", url, headers=headers, data=data)

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