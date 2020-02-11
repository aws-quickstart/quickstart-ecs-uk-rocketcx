import json
import os
from botocore.vendored import requests


def lambda_handler(event, context):
    '''
    :summary: Function calls below mentioned rest API endpoints from RocketCX Enterprise Connector for ServiceNow.
            'api/x_ecsd_amazon_conn/connect_cti_api/user'

            This API accepts caller's phone number as input and returns details for all users associated
            with phone number from SNOW. 
            For more details on API please refer to API documentaiton.
    :input: Caller Phone number from call flow.
    :output: A JSON with caller details.
            "record_found": 0/1, (1= caller phone number is associated with one or more users in SNOW DB.)
            "customer_name": customer_name, (customer name = none if caller number is associated with none or
                                             multiple users in SNOW DB else returns customer name.)
            "duplicate_contact": 0/1, (1 = caller number is associated with multiple users in SNOW DB)
          
    '''

    url: str = os.environ['SERVICENOW_HOST']
    servicenow_user: str = os.environ['SERVICENOW_USER']
    servicenow_password: str = os.environ['SERVICENOW_PASSWORD']
    customer_phone: str = ''
    customer_name: str = ''
    return_object: dict = {}
    record_found: int = 0
    duplicate_contact: int = 0

    customer_phone = event['Details']['Parameters']['Phone']

    url_with_extension = url + 'api/x_ecsd_amazon_conn/connect_cti_api/' \
                         + f'user?contact_number={customer_phone}'

    headers = {"Accept": "application/json"}

    response = requests.get(url_with_extension, auth=(servicenow_user,servicenow_password), headers=headers)

    if "Error" in response.json()["result"]:
        customer_name = "none"
        record_found = 0
        duplicate_contact = 0
    elif response.json()["result"]["duplicateContact"] == "false" and response.json()["result"]["userCount"] == 1:
        customer_name = response.json()["result"]["usersDetails"][0]["callerName"]
        record_found = 1
        duplicate_contact = 0
    elif response.json()["result"]["duplicateContact"] == "true" and response.json()["result"]["userCount"] > 1:
        customer_name = "none"
        record_found = 1
        duplicate_contact = 1


    return_object = {
        "record_found": record_found,
        "customer_name": customer_name,
        "duplicate_contact": duplicate_contact,

    }

    return return_object

