import logging
import os

import azure.cosmos.cosmos_client as cosmos_client
import azure.functions as func
import azure.cosmos.exceptions as exceptions

HOST = os.environ.get('ACCOUNT_HOST')
MASTER_KEY = os.environ.get('ACCOUNT_KEY')
DATABASE_ID = os.environ.get('COSMOS_DATABASE')
CONTAINER_ID = os.environ.get('COSMOS_CONTAINER')


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    key = req.params.get('key')

    if key:
        logging.info(f'ReadStateDatabase was called with key {key}.')

        client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY},
                                            user_agent="CosmosDBDotnetQuickstart",
                                            user_agent_overwrite=True)
        try:
            database = client.get_database_client(DATABASE_ID)
            container = database.get_container_client(CONTAINER_ID)
            state = container.read_item(item=key, partition_key=key)
            logging.info(f'State read {state}.')

        except exceptions.CosmosHttpResponseError as e:
            logging.error('ReadStateDatabase has caught an error. {0}'.format(e.message))
            return func.HttpResponse(f'No entry found for key {key}', status_code=404)

        finally:
            logging.info('ReadStateDatabase finished.')

        return func.HttpResponse(state['payload'])

    else:
        return func.HttpResponse(
            "Pass a key in the query string or in the request body.",
            status_code=200
        )
