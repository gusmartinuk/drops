import requests
import json
import base64
import hashlib
import hmac
import time
import urllib.parse
from xml.etree import ElementTree
from config import *


# Helper functions for signing requests
def sign_request(string_to_sign, amz_date, region, service):
    k_date = hmac.new(("AWS4" + AWS_SECRET_KEY).encode('utf-8'), amz_date[:8].encode('utf-8'), hashlib.sha256).digest()
    k_region = hmac.new(k_date, region.encode('utf-8'), hashlib.sha256).digest()
    k_service = hmac.new(k_region, service.encode('utf-8'), hashlib.sha256).digest()
    k_signing = hmac.new(k_service, b'aws4_request', hashlib.sha256).digest()
    return hmac.new(k_signing, string_to_sign.encode('utf-8'), hashlib.sha256).digest()

def generate_sts_headers(host, amz_date, region, service):
    canonical_request = f"GET\n/\nAction=AssumeRole&DurationSeconds=3600&RoleArn=arn:aws:iam::288492343985:role/selleraccessrole&RoleSessionName=spsession1&Version=2011-06-15\nhost:{host}\nx-amz-date:{amz_date}\n\nhost;x-amz-date\nUNSIGNED-PAYLOAD"
    string_to_sign = f"AWS4-HMAC-SHA256\n{amz_date}\n{amz_date[:8]}/{region}/{service}/aws4_request\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"

    signature = sign_request(string_to_sign, amz_date, region, service)

    headers = {
        'X-Amz-Date': amz_date,
        'Authorization': f"AWS4-HMAC-SHA256 Credential={AWS_ACCESS_KEY}/{amz_date[:8]}/{region}/{service}/aws4_request, SignedHeaders=host;x-amz-date, Signature={signature.hex()}",
        'host': host
    }
    return headers

def assume_role():
    url = "https://sts.amazonaws.com/"
    query_string = "Version=2011-06-15&Action=AssumeRole&RoleSessionName=spsession1&RoleArn=arn:aws:iam::288492343985:role/selleraccessrole&DurationSections=3600"
    host = "sts.amazonaws.com"
    amz_date = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    region = "us-east-1"
    service = "sts"

    headers = generate_sts_headers(host, amz_date, region, service)
    response = requests.get(url + "?" + query_string, headers=headers)

    if response.status_code == 200:
        return response.text
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

def get_inventory(access_key, secret_key, session_token):
    method = "GET"
    host = "sellingpartnerapi-eu.amazon.com"
    path = "/catalog/v0/items"
    query_string = f"SellerId={ySELLER_ID}&MarketplaceId={MARKETPLACE_ID}&MWSAuthToken={MWS_AUTH_TOKEN}"
    region = "eu-west-1"
    service = "execute-api"
    amz_date = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    date_stamp = amz_date[:8]

    canonical_request = f"{method}\n{path}\n{query_string}\nhost:{host}\nx-amz-date:{amz_date}\nx-amz-security-token:{session_token}\n\nhost;x-amz-date;x-amz-security-token\nUNSIGNED-PAYLOAD"
    string_to_sign = f"AWS4-HMAC-SHA256\n{amz_date}\n{date_stamp}/{region}/{service}/aws4_request\n{hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()}"
    signature = sign_request(string_to_sign, amz_date, region, service)

    headers = {
        "Host": host,
        "X-Amz-Date": amz_date,
        "X-Amz-Security-Token": session_token,
        "Authorization": f"AWS4-HMAC-SHA256 Credential={access_key}/{date_stamp}/{region}/{service}/aws4_request, SignedHeaders=host;x-amz-date;x-amz-security-token, Signature={signature.hex()}",
    }

    url = f"https://{host}{path}?{query_string}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")

if __name__ == "__main__":
    try:
        sts_response = assume_role()
        tree = ElementTree.fromstring(sts_response)
        namespace = {'aws': 'https://sts.amazonaws.com/doc/2011-06-15/'}

        access_key = tree.find('.//aws:AccessKeyId', namespace).text
        secret_key = tree.find('.//aws:SecretAccessKey', namespace).text
        session_token = tree.find('.//aws:SessionToken', namespace).text

        #inventory = get_inventory(access_key, secret_key, session_token)
        #print(json.dumps(inventory, indent=2))
    except Exception as e:
        print(e)
