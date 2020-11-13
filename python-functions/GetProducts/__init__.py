import logging
import json

import azure.functions as func

import logging
import os
import pyodbc
import requests 
import struct
import sys

resource_uri="https://database.windows.net/"
sql_server="subtracker.database.windows.net"
sql_database="subtracker"

def get_bearer_token(resource_uri):
    identity_endpoint = os.environ["IDENTITY_ENDPOINT"]
    identity_header = os.environ["IDENTITY_HEADER"]
    logging.info('identity_endpoint: {}'.format(identity_endpoint))
    logging.info('identity_header : {}'.format(identity_header))
    token_auth_uri = f"{identity_endpoint}?resource={resource_uri}&amp;api-version=2017-09-01"
    head_msi = {'X-IDENTITY-HEADER':identity_header}
    resp = requests.get(token_auth_uri, headers=head_msi)
    access_token = resp.json()['access_token']
    logging.info('response received from token endpoint: {}'.format(access_token))
    return access_token  
 
def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Function Starting')
    try:
        access_token = get_bearer_token(resource_uri)
        accessToken = bytes(access_token, 'utf-8')
        exptoken = b""
        for i in accessToken:
                exptoken += bytes({i})
                exptoken += bytes(1)
        tokenstruct = struct.pack("=i", len(exptoken)) + exptoken  
        conn = pyodbc.connect("Driver={ODBC Driver 17 for SQL Server};Server=tcp:{},1433;Database={}".format(sql_server,sql_database), attrs_before = { 1256:bytearray(tokenstruct) })
        logging.info('connected to {} on {}'.format(sql_server,sql_database))
        cursor = conn.cursor()
        cursor.execute("select @@version")
        row = cursor.fetchall()
        logging.info('sql data: {}'.format(row[0])) 
        logging.info('finished')              
    except BaseException as error:
        logging.info('An exception occurred: {}'.format(error))   
    return func.HttpResponse("done!")

