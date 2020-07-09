import requests
import os
import json

api_url = os.environ.get('PORTAL_API_URL')
user = os.environ.get('PORTAL_USER')
password = os.environ.get('PORTAL_PASSWORD')
dgfip_api_id = os.environ.get('DGFIP_API_ID')
caf_api_id = os.environ.get('CAF_API_ID')
dgfip_plan_id = os.environ.get('DGFIP_PLAN_ID')
caf_plan_id = os.environ.get('CAF_PLAN_ID')

assert api_url is not None
assert user is not None
assert password is not None
assert dgfip_api_id is not None
assert caf_api_id is not None
assert dgfip_plan_id is not None
assert caf_plan_id is not None

base_url = '{}/management/organizations/DEFAULT/environments/DEFAULT'.format(api_url)

with open('tokens.json') as tokens_file:
    tokens = json.load(tokens_file)
    for token in tokens:
        if 'signup_id' not in token or 'hashed_token' not in token:
            continue

        application_request = requests.post('{}/applications'.format(base_url), json={
            'name': token['name'],
            'description': 'Numéro de demande : {}'.format(token['signup_id']),
            'type': 'web',
            'clientId': token['hashed_token']
        }, auth=(user, password))
        if application_request.status_code == 400:
            continue

        assert application_request.ok
        application = application_request.json()

        subscription_dgfip_request = requests.post('{}/applications/{}/subscriptions'.format(base_url, application['id']), params={'plan': dgfip_plan_id}, auth=(user, password))
        assert subscription_dgfip_request.ok
        subscription_dgfip = subscription_dgfip_request.json()

        subscription_caf_request = requests.post('{}/applications/{}/subscriptions'.format(base_url, application['id']), params={'plan': caf_plan_id}, auth=(user, password))
        assert subscription_caf_request.ok
        subscription_caf = subscription_caf_request.json()

        accept_dgfip_subscription_request = requests.post('{}/apis/{}/subscriptions/{}/_process'.format(base_url, dgfip_api_id, subscription_dgfip['id']), json={'accepted': True}, auth=(user, password))
        assert accept_dgfip_subscription_request.ok
        accept_caf_subscription_request = requests.post('{}/apis/{}/subscriptions/{}/_process'.format(base_url, caf_api_id, subscription_caf['id']), json={'accepted': True}, auth=(user, password))
        assert accept_caf_subscription_request.ok
