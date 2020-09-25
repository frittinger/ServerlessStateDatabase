import datetime
import logging
import uuid
import os

import azure.cosmos.cosmos_client as cosmos_client
import azure.functions as func
import azure.cosmos.exceptions as exceptions

settings = {
    'host': os.environ.get('ACCOUNT_HOST', 'https://serverless-state-database-fr.documents.azure.com:443/'),
    'master_key': os.environ.get('ACCOUNT_KEY', 'ahcimd2reQgQeBfuZxnE1Ffcfq04kuZRA2sREtS4NmRAXUpx4po2GOejobmgS8g9YKF6SQlOympLmeRKJ0eoOA=='),
    'database_id': os.environ.get('COSMOS_DATABASE', 'States'),
    'container_id': os.environ.get('COSMOS_CONTAINER', 'Data'),
}

HOST = settings['host']
MASTER_KEY = settings['master_key']
DATABASE_ID = settings['database_id']
CONTAINER_ID = settings['container_id']


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        logging.info(f'WriteStateDatabase was called with data {name}.')
        state = create_state(name)
        logging.info(f'State created {state}.')

        client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY},
                                            user_agent="CosmosDBDotnetQuickstart",
                                            user_agent_overwrite=True)
        try:
            database = client.get_database_client(DATABASE_ID)
            container = database.get_container_client(CONTAINER_ID)
            container.create_item(state)
        except exceptions.CosmosHttpResponseError as e:
            logging.error('WriteStateDatabase has caught an error. {0}'.format(e.message))
            return func.HttpResponse("Your request could not be processed", status_code=500)

        finally:
            logging.info('WriteStateDatabase finished.')

        return func.HttpResponse(f"Your data was stored with key {state.get('id')}.")

    else:
        return func.HttpResponse(
             "Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )


def create_state(data):
    key = str(uuid.uuid4())
    state = {'id': key,
             'created_by': 'FR',
             'created_at': str(datetime.datetime.now()),
             'key': key,
             'payload': data
             }

    return state
