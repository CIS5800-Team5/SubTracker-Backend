from flask import Flask
from flask import request, jsonify

import logging
import os
import azure.functions as func
import pyodbc
import requests 
import struct

msi_endpoint = os.environ["MSI_ENDPOINT"]
msi_secret = os.environ["MSI_SECRET"]

resource_uri="https://database.windows.net/"
sql_server="subtracker.database.windows.net"
sql_database="subtracker"
 

app = Flask(__name__)

# Create some test data for our catalog in the form of a list of dictionaries.
books = [
    {'id': 0,
     'title': 'A Fire Upon the Deep',
     'author': 'Vernor Vinge',
     'first_sentence': 'The coldsleep itself was dreamless.',
     'year_published': '1992'},
    {'id': 1,
     'title': 'The Ones Who Walk Away From Omelas',
     'author': 'Ursula K. Le Guin',
     'first_sentence': 'With a clamor of bells that set the swallows soaring, the Festival of Summer came to the city Omelas, bright-towered by the sea.',
     'published': '1973'},
    {'id': 2,
     'title': 'Dhalgren',
     'author': 'Samuel R. Delany',
     'first_sentence': 'to wound the autumnal city.',
     'published': '1975'}
]


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Distant Reading Archive</h1>
<p>A prototype API for distant reading of science fiction novels.</p>'''

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



@app.route('/api/v1/resources/books/all', methods=['GET'])
def api_all():
    return jsonify(books)


@app.route('/api/v1/resources/books', methods=['GET'])
def api_id():
    # Check if an ID was provided as part of the URL.
    # If ID is provided, assign it to a variable.
    # If no ID is provided, display an error in the browser.
    if 'id' in request.args:
        id = int(request.args['id'])
    else:
        return "Error: No id field provided. Please specify an id."

    # Create an empty list for our results
    results = []

    # Loop through the data and match results that fit the requested ID.
    # IDs are unique, but other fields might return many results
    for book in books:
        if book['id'] == id:
            results.append(book)

    # Use the jsonify function from Flask to convert our list of
    # Python dictionaries to the JSON format.
    return jsonify(results)