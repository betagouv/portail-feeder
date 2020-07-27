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
scopes_dictionary_id = os.environ.get('SCOPES_DICTIONARY_ID')
application_names_dictionary_id = os.environ.get('APPLICATION_NAMES_DICTIONARY_ID')

assert api_url is not None
assert user is not None
assert password is not None
assert dgfip_api_id is not None
assert caf_api_id is not None
assert dgfip_plan_id is not None
assert caf_plan_id is not None
assert scopes_dictionary_id is not None
assert application_names_dictionary_id is not None

base_url = '{}/management/organizations/DEFAULT/environments/DEFAULT'.format(api_url)

with open('tokens.json') as tokens_file:
    tokens = json.load(tokens_file)

    # First create the applications
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

        subscription_dgfip_request = requests.post('{}/apis/{}/subscriptions'.format(base_url, dgfip_api_id), params={'plan': dgfip_plan_id, 'application': application['id']}, auth=(user, password))
        assert subscription_dgfip_request.ok

        subscription_caf_request = requests.post('{}/apis/{}/subscriptions'.format(base_url, caf_api_id), params={'plan': caf_plan_id, 'application': application['id']}, auth=(user, password))
        assert subscription_caf_request.ok

    # Update the scopes and application names dictionaries
    applications_request = requests.get('{}/applications'.format(base_url), auth=(user, password))
    assert applications_request.ok
    applications = applications_request.json()

    scopes_dictionary = {}
    application_names_dictionary = {}

    for application in applications:
        for token in tokens:
            if 'hashed_token' in token and 'client_id' in application['settings'] and token['hashed_token'] == application['settings']['client_id']:
                scopes_dictionary[token['hashed_token'][0:64]] = ",".join(token['scopes'])
                application_names_dictionary[application['id']] = application['name']

    update_scopes_dictionary_request = requests.put('{}/configuration/dictionaries/{}'.format(base_url, scopes_dictionary_id), json={
        'name': 'API-Particulier Scopes',
        'type': 'MANUAL',
        'properties': scopes_dictionary
    }, auth=(user, password))
    assert update_scopes_dictionary_request.ok

    update_application_names_dictionary_request = requests.put('{}/configuration/dictionaries/{}'.format(base_url, application_names_dictionary_id), json={
        'name': 'Application Names',
        'type': 'MANUAL',
        'properties': application_names_dictionary
    }, auth=(user, password))
    assert update_application_names_dictionary_request.ok
