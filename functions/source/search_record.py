import json
import os
from botocore.vendored import requests

def lambda_handler(event, context):
    '''
    :summary: Function calls different rest API endpoints from RocketCX Enterprise Connector for ServiceNow.
            'api/x_ecsd_amazon_conn/connect_cti_api/incident/',
            'api/x_ecsd_amazon_conn/connect_cti_api/hr_case/',
            'api/x_ecsd_amazon_conn/connect_cti_api/csm_case/'

            These API endopints accepts record number as input and returns detils ofomatching record.
            For more details on API please refer to API documentaiton.

    :input: record number to search in related module like incident, hr-case or csm-case.
    :output: JSON with record details.
    '''

    url: str = os.environ['SERVICENOW_HOST']
    servicenow_user: str = os.environ['SERVICENOW_USER']
    servicenow_password: str = os.environ['SERVICENOW_PASSWORD']
  
    return_object: dict = {}
    record_found: int = 0
    record_count: int = 0
    multi_record: int = 0
    record_subject: str = ""
    record_type: str = ""
    open_date: str = ""
    last_open_date: str = ""
    last_record_subject: str = ""

    record_number = event['Details']['Parameters']['record_number']
  
    headers = {"Accept": "application/json"}

    '''
    RocketCX Enterprise Connector for ServiceNow provides different API endpoints 
    to search record in modules like incident, hr-case and csm-case as demonstrated 
    in below example.
    '''
    
    # search for record in incidents.
    url_with_extension = url + f'api/x_ecsd_amazon_conn/connect_cti_api/incident/{record_number}'
    record_found,last_record_subject,last_open_date = check_record(url_with_extension,servicenow_user, servicenow_password, headers)
    if record_found ==1: 
        record_count = record_count + 1
        record_type="Incident"
        record_subject,open_date = last_record_subject, last_open_date
    
    # search for record in HR case.
    url_with_extension = url + f'api/x_ecsd_amazon_conn/connect_cti_api/hr_case/{record_number}'
    record_found=0
    record_found,last_record_subject,last_open_date = check_record(url_with_extension,servicenow_user, servicenow_password, headers)
    if record_found ==1: 
        record_count = record_count + 1
        record_type="HR-Case"
        record_subject,open_date = last_record_subject, last_open_date
     
    # search for record in CSM case.
    url_with_extension = url + f'api/x_ecsd_amazon_conn/connect_cti_api/csm_case/{record_number}'
    record_found=0
    record_found,last_record_subject,last_open_date = check_record(url_with_extension, servicenow_user, servicenow_password, headers)
    if record_found ==1: 
        record_count = record_count + 1
        record_type="CSM-Case"
        record_subject,open_date = last_record_subject, last_open_date
    
    if record_count > 1:
        multi_record = 1
        record_found = 1
        record_subject = "None"
        record_open_date = "None"
    if record_count == 1:
        multi_record = 0
        record_found = 1
        record_subject = record_subject
        record_open_date = open_date
    if record_found == 0 :
        multi_record = 0
        record_found = 0
        record_subject = "None"
        record_open_date = "None"
     
     
    return_object = {
        "record_number": record_number,
        "multi_record": multi_record,
        "record_found": record_found,
        "record_type": record_type,
        "record_subject": record_subject,
        "record_open_date": record_open_date
        } 
        
    return return_object

def check_record(url,servicenow_user, servicenow_password, headers):
    
    response = requests.get(url,auth=(servicenow_user,servicenow_password), headers=headers)
    
    if "Error" in response.json()["result"]:
        record_found = 0
        record_subject = "None"
        open_date = "None"
    elif (response.json()["result"]["number"]) :
        record_found = 1
        record_subject = response.json()["result"]["short_description"]
        if len(record_subject) < 1:
            record_subject = "Not available"
        open_date = response.json()["result"]["open_date"]
        
    return record_found,record_subject,open_date
