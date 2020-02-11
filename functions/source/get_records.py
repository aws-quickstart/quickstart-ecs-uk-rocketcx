import json
import os
from botocore.vendored import requests

def lambda_handler(event, context):
    '''
    :summary: Function calls below mentioned rest API endpoints from RocketCX Enterprise Connector for ServiceNow.
            'api/x_ecsd_amazon_conn/connect_cti_api/record' 

            This API accepts caller's phone number, name and record state as input and returns detils for
            matching records. 
            For more details on API please refer to API documentaiton.
    :input: Caller Phone number, caller name, record state = active from call flow.
    :output: A JSON with record details.
            "active_record_found": 0/1, 
            "customer_name": name of record user.
            "open_record_count": number of open records associated with caller phone number
            "record_type_list": list of returned record types separated by '-----'
            "record_number_list": list of returned record numbers separated by '-----'
            "record_subject_list": list of returned record summary separated by '-----'
            "record_open_date_list": list of returned record opend dates seperated by '-----'
    '''

    url: str = os.environ['SERVICENOW_HOST']
    servicenow_user: str = os.environ['SERVICENOW_USER']
    servicenow_password: str = os.environ['SERVICENOW_PASSWORD']
    customer_phone: str = ''
    customer_name: str = ''
    return_object: dict = {}
    record_found: int = 0
    incident_count: int = 0
    hrcase_count: int = 0
    csmcase_count: int = 0
    record_number_list: str = ""
    record_subject_list: str = ""
    record_type_list: str = ""
    record_open_date_list: str = ""

    customer_phone = event['Details']['Parameters']['Phone']
    customer_name =  event['Details']['Parameters']['Name']

    url_with_extension = url + 'api/x_ecsd_amazon_conn/connect_cti_api/record?' \
                        + f'active=true&contact_number={customer_phone}&caller_name={customer_name}'
                        
    headers = {"Accept": "application/json"}

    response = requests.get(url_with_extension, auth=(servicenow_user,
                                                      servicenow_password), headers=headers)
    
    if "Error" in response.json()["result"]:
        customer_name = "None"
        record_found = 0
        incident_count = 0
        hrcase_count = 0
        csmcase_count = 0
        record_number_list = "None"
        record_subject_list = "None"
        record_type_list = "None"
        record_open_date_list = "None"
    elif (int(response.json()["result"]["usersDetails"]["incident"]) > 0 or 
            int(response.json()["result"]["usersDetails"]["hrcase"]) > 0 or 
            int(response.json()["result"]["usersDetails"]["csmcase"]) > 0):
        customer_name = response.json()["result"]["usersDetails"]["callerName"]
        record_found = 1
        incident_count = int(response.json()["result"]["usersDetails"]["incident"])
        hrcase_count = int(response.json()["result"]["usersDetails"]["hrcase"])
        csmcase_count = int(response.json()["result"]["usersDetails"]["csmcase"])
        record_number_list, record_subject_list, record_type_list,record_open_date_list \
        = extract_record_details(response.json()["result"]["usersDetails"], \
        record_number_list, record_subject_list, record_type_list, record_open_date_list)
    elif (int(response.json()["result"]["usersDetails"]["incident"]) == 0 and 
            int(response.json()["result"]["usersDetails"]["hrcase"]) == 0 and 
            int(response.json()["result"]["usersDetails"]["csmcase"]) == 0):
        customer_name = response.json()["result"]["usersDetails"]["callerName"]
        record_found = 1        
        incident_count = 0
        hrcase_count = 0
        csmcase_count = 0
        record_number_list = "None"
        record_subject_list = "None"
        record_type_list = "None"
        record_open_date_list = "None"
        

   
                
    return_object = {
    "record_found": record_found,
    "customer_name": customer_name,
    "open_record_count": incident_count + hrcase_count + csmcase_count,
    "record_type_list": record_type_list,
    "record_number_list": record_number_list,
    "record_subject_list": record_subject_list,
    "record_open_date_list": record_open_date_list
    }

    return return_object

    

def extract_record_details(user_details, record_number_list, record_subject_list, record_type_list,record_open_date_list):

    for recorddetail in user_details["recordDetails"]:
        record_type = recorddetail

        for record in user_details["recordDetails"][recorddetail]:
            record_number = record["number"]
            open_date = record["open_date"]
            if len(record["short_description"]) < 1:
                record_subject = "Not available"
            else:
                record_subject = record["short_description"]


            record_type_list = record_type_list + "-----" + record_type
            record_number_list = record_number_list + "-----" + record_number
            record_subject_list = record_subject_list + "-----" + record_subject
            record_open_date_list = record_open_date_list + "-----" + open_date
                
    return record_number_list.replace("-----", "", 1), record_subject_list.replace("-----", "", 1) \
        , record_type_list.replace("-----", "", 1), record_open_date_list.replace("-----", "", 1)
