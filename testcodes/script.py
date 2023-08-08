from sp_api.api import Products
from sp_api.api import Sellers
from sp_api.base import Marketplaces, SellingApiException
import boto3
from config import *

# https://sp-api-docs.saleweaver.com/quickstart/#example-usage
# Replace these with your own access and secret keys

session = boto3.Session(
    aws_access_key_id=xAWS_ACCESS_KEY,
    aws_secret_access_key=xAWS_SECRET_KEY,
    region_name="us-east-1"
)

"""
sts_client = session.client('sts',region_name='eu-west-2')
response = sts_client.assume_role(
    RoleArn=ROLE_ARN,
    RoleSessionName="spseesion1",
    DurationSeconds=3600
)

access_key_id = response['Credentials']['AccessKeyId']
secret_access_key = response['Credentials']['SecretAccessKey']
session_token = response['Credentials']['SessionToken']
"""

sts_client = session.client('sts',region_name='eu-west-2')
response = sts_client.get_session_token(        
    DurationSeconds=3600
)
print(response['Credentials'])

access_key_id = response['Credentials']['AccessKeyId']
secret_access_key = response['Credentials']['SecretAccessKey']
session_token = response['Credentials']['SessionToken']

#access_key_id = AWS_ACCESS_KEY
#secret_access_key = AWS_SECRET_KEY


credentials = dict(
    aws_access_key=access_key_id,
    aws_secret_key=secret_access_key,
    aws_session_token=session_token,
    lwa_app_id=xLWA_APP_ID,
    lwa_client_secret=xCLIENT_SECRET,
    refresh_token=xREFRESH_TOKEN
)
print(credentials)





"""
sellers_api = Sellers(marketplace=Marketplaces.GB, credentials=credentials,account=SELLER_ID)    
response=sellers_api.get_marketplace_participation()
print(response)

try:
    orders_api = Orders(marketplace=Marketplaces.GB, credentials=credentials,account=SELLER_ID)    
    response=orders_api.get_orders()
    print(response)
    print("\n")

except SellingApiException as e:
    print(f"Error: {e}")


"""
asin_list = ['B07FZXTDJW', 'B09J21BQVN']
marketplace_id = "A1F83G8C2ARO7P"
item_type = 'Asin'  # Use 'Sku' for SKU values
item_condition = 'New'  # You can change this to the desired item condition

try:
    products_api = Products(marketplace=Marketplaces.GB, credentials=credentials,account=SELLER_ID)
    
    for asin in asin_list:
        response = products_api.get_product_pricing_for_asins(            
            asin_list=[asin],
            ItemType=item_type,
            ItemCondition=item_condition
        )
        print(f"Pricing Information for ASIN {asin}:")
        print(response)
        print("\n")

except SellingApiException as e:
    print(f"Error: {e}")




