from sp_api.api import Orders
from sp_api.api import Tokens
from sp_api.base import AccessTokenClient, Marketplaces
from sp_api.auth import Credentials
from sp_api.base.credential_provider import CredentialProvider, FromCodeCredentialProvider
import yaml
import confuse
import os

def refresh_access_token(credentials):
    tokens_api = Tokens(credentials=credentials)
    result = tokens_api.create_restricted_data_token(
        restrictedResources=[
            {
                'method': 'GET',
                'path': '/orders/v0/orders',
                'dataElements': ['buyerInfo', 'shippingAddress']
            }
        ],
        access_token=AccessTokenClient(credentials)
    )
    return result.payload

def load_sp_api_credentials(account):  # default or root
    with open('testcodes\credentials.yml', 'r') as file:
        credentials = yaml.safe_load(file)

    xcredentials = {
        "aws_access_key": credentials[account]["aws_access_key"],
        "aws_secret_key": credentials[account]["aws_secret_key"],
        "lwa_app_id": credentials[account]["lwa_app_id"],
        "lwa_client_secret": credentials[account]["lwa_secret_key"],
        "refresh_token": credentials[account]["refresh_token"],       
        "role_arn": credentials[account]["aws_role_arn"]
    }   
    return xcredentials

credentials = load_sp_api_credentials('default')
credentials_provider = CredentialProvider(
    account="default",
    credentials=credentials,
    credential_providers=[FromCodeCredentialProvider]
)
print("****credentials******")
print(credentials)
print("**********")

response = Orders().get_orders(credentials=credentials,CreatedAfter='TEST_CASE_200', MarketplaceIds=["ATVPDKIKX0DER"])
print(response)

exit()
tokcredentials = Credentials(
    refresh_token=credentials["refresh_token"],
    credentials=credentials
)

refreshed_token = refresh_access_token(tokcredentials)
print("****refreshed token******")
print(refreshed_token)
print("**********")

order_client = Orders(credentials=tokcredentials, marketplace=Marketplaces.GB)
order = order_client.get_order('205-0173297-9295570')
print(order) # `order` is an `ApiResponse`
print(order.payload) # `payload` contains the original response
