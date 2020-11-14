from flask import Flask
from flask import request, jsonify
import mysql.connector

mysql_server="subtracker-db.mysql.database.azure.com"
sql_database="subtracker_api"

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return '''<h1>Distant Reading Archive</h1>
<p>A prototype API for distant reading of science fiction novels.</p>'''

@app.route('/api/services/all', methods=['GET'])
def get():
    cnx = mysql.connector.connect(user="sql_admin", password=sql_password, host="subtracker-db.mysql.database.azure.com", port=3306, database="subtracker_api", ssl_ca="./DigiCertGlobalRootCA.crt.pem")
    cursor = cnx.cursor()
    cur.execute('''select * from services''')
    r = [dict((cur.service_name[i][0], value)
              for i, value in enumerate(row)) for row in cur.fetchall()]
    return jsonify(r)

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