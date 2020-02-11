import json
import os
import datetime
from botocore.vendored import requests


def lambda_handler(event, context):

    '''
    :summary: Function calls below mentioned rest API endpoints from RocketCX Enterprise Connector for ServiceNow.
            api/x_ecsd_amazon_conn/connect_cti_api/survey
            
            This API accepts caller phone number, survey points (1-5) and Amazon connect call ID for which
            survey feedback needs to be recorded.
            For more details on API please refer to API documentaiton.
    :input: record number and survey points form call flow
    :output: status code of 200 on sucessfull update of SNOW call log table.
    '''

    url: str = os.environ['SERVICENOW_HOST']
    servicenow_user: str = os.environ['SERVICENOW_USER']
    servicenow_password: str = os.environ['SERVICENOW_PASSWORD']

    phone : int = event['Details']['Parameters']['Phone']
    survey_points : int = event['Details']['Parameters']['Survey_Points']
    call_id : str = event['Details']['Parameters']['Call_Id']

    url_with_extension = url + f'api/x_ecsd_amazon_conn/connect_cti_api/survey'
    
    headers = {"Accept": "application/json"}

    survey_data = {"phone_no": phone, "point" : survey_points, "call_id" : call_id} 

    response = requests.patch(url_with_extension, data=json.dumps(survey_data), auth=(servicenow_user, servicenow_password), headers=headers)

    if response.status_code == 200:
        return {'survey_update_status' : 1}
    else:
        return {'survey_update_status' : 0}
