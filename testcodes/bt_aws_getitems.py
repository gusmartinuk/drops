import boto3
from requests_aws4auth import AWS4Auth
import requests

# Set up the STS client
sts_client = boto3.client('sts')

# Assume the IAM role and get temporary credentials
assumed_role = sts_client.assume_role(RoleArn='{{role_arn}}', RoleSessionName='spsession1', DurationSeconds=3600)
creds = assumed_role['Credentials']

# Set up the AWS4 authentication object
auth = AWS4Auth(creds.access_key, creds.secret_key, 'us-west-1', 'execute-api', session_token=creds.token)

# Make a request to the Selling Partner API
response = requests.get('{{selling_partner_api_endpoint}}', auth=auth)

# Print the response
print(response.json())