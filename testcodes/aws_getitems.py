import requests
import json
from requests_aws4auth import AWS4Auth

from config import *
def gettoken():
    auth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, 'us-east-1', 'sts')
    return(auth)



# Get Inventory
def get_inventory():
    auth=gettoken()
    sp = 'https://sellingpartnerapi-eu.amazon.com'
    url = f"{sp}/catalog/2020-12-01/items"
    headers = {
        'x-amz-access-token': MWS_AUTH_TOKEN,
        'x-amz-marketplace-id': MARKETPLACE_ID,
        'x-amz-seller-id': SELLER_ID,
    }

    auth = AWS4Auth(AWS_ACCESS_KEY, AWS_SECRET_KEY, 'eu-west-1', 'execute-api')
    response = requests.get(url, auth=auth, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Error: {response.text}")

    return response.json()['items']

if __name__ == "__main__":
    try:
        inventory = get_inventory()
        print(json.dumps(inventory, indent=2))
    except Exception as e:
        print(e)
