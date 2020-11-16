from flask import Flask
from flask import request, jsonify
import pymysql
import os

mysql_server="subtracker-db.mysql.database.azure.com"
sql_database="subtracker_api"
sql_user='sql_admin'
sql_pass=os.environ['sql_pass']

cnx = pymysql.connect(user=sql_user, passwd=sql_pass, host=mysql_server, database=sql_database,ssl={'ca': 'DigiCertGlobalRootCA.crt.pem'})

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return '''<p><pre>
________________
 ____        _   _____               _             
/ ___| _   _| |_|_   _| __ __ _  ___| | _____ _ __ 
\___ \| | | | '_ \| || '__/ _` |/ __| |/ / _ \ '__|
 ___) | |_| | |_) | || | | (_| | (__|   <  __/ |   
|____/ \__,_|_.__/|_||_|  \__,_|\___|_|\_\___|_|   
                  ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
   _____ __________.___ 
  /  _  \\______   \   |
 /  /_\  \|     ___/   |
/    |    \    |   |   |
\____|__  /____|   |___|
        \/              
</pre><p>An API for using the SubTracker application</p>'''

@app.route('/api/services/all', methods=['GET'])
def get_services_all():
    cur = cnx.cursor()
    cur.execute('''select * from services''')
    data = [dict((cur.description[idx][0], value) 
                for idx, value in enumerate(row)) for row in cur.fetchall()]
    return jsonify(data)

@app.route('/api/services/search', methods=['GET'])
def get_services():
    query_parameters = request.args

    service_id = query_parameters.get('service_id')
    service_name = query_parameters.get('service_name')

    query = "SELECT * FROM services WHERE"
    to_filter = []

    if service_id:
        query += ' service_id=%s AND'
        to_filter.append(service_id)
    if service_name:
        query += ' service_name=%s AND'
        to_filter.append(service_name)
    if not (id or name):
        return page_not_found(404)

    query = query[:-3] + ';'
    cur = cnx.cursor()
    cur.execute(query, to_filter)
    data = [dict((cur.description[idx][0], value) 
                for idx, value in enumerate(row)) for row in cur.fetchall()]
    return jsonify(data)
    #return str(query)

@app.route('/api/subscriptions', methods=['GET'])
def get_subscriptions():
    cur = cnx.cursor()
    cur.execute('''select * from subscriptions''')
    data = [dict((cur.description[idx][0], value) 
                for idx, value in enumerate(row)) for row in cur.fetchall()]
    return jsonify(data)

@app.route('/api/customers/all', methods=['GET'])
def get_customers_all():
    cur = cnx.cursor()
    cur.execute('''select * from customers''')
    data = [dict((cur.description[idx][0], value) 
                for idx, value in enumerate(row)) for row in cur.fetchall()]
    return jsonify(data)

@app.route('/api/customers/search', methods=['GET'])
def get_customers():
    query_parameters = request.args

    customer_id = query_parameters.get('customer_id')
    customer_email = query_parameters.get('customer_email')
    customer_phone = query_parameters.get('customer_phone')
    customer_status = query_parameters.get('customer_status')

    query = "SELECT * FROM services WHERE"
    to_filter = []

    if customer_id:
        query += ' customer_id=%s AND'
        to_filter.append(customer_id)
    if customer_email:
        query += ' customer_email=%s AND'
        to_filter.append(customer_email)
    if customer_phone:
        query += ' customer_phone=%s AND'
        to_filter.append(customer_phone)
    if customer_status:
        query += ' customer_status=%s AND'
        to_filter.append(customer_status)
    if not (customer_id or customer_email or customer_phone):
        return page_not_found(404)

    query = query[:-3] + ';'
    cur = cnx.cursor()
    cur.execute(query, to_filter)
    data = [dict((cur.description[idx][0], value) 
                for idx, value in enumerate(row)) for row in cur.fetchall()]
    return jsonify(data)
    #return str(query)

@app.route('/api/customers/create', methods=['GET']) ##This should be a POST 
def create_customers():
    query_parameters = request.args

    customer_oauth_id = query_parameters.get('customer_oauth_id')
    customer_email = query_parameters.get('customer_email')
    customer_phone = query_parameters.get('customer_phone')
    customer_status = query_parameters.get('customer_status')
    customer_firstname = query_parameters.get('customer_firstname')
    customer_lastname = query_parameters.get('customer_lastname')

    query = "INSERT INTO customers Values ("
    to_filter = []

    if customer_email:
        query += ' customer_email, '
        to_filter.append(customer_email)
    if customer_oauth_id:
        query += ' customer_oauth_id, '
        to_filter.append(customer_oauth_id)
    if customer_firstname:
        query += ' customer_firstname, '
        to_filter.append(customer_firstname)
    if customer_lastname:
        query += ' customer_lastname, '
        to_filter.append(customer_lastname)
    if customer_phone:
        query += ' customer_phone, '
        to_filter.append(customer_phone)
    if customer_status:
        query += ' customer_status, '
        to_filter.append(customer_status)
    if not (customer_oauth_id or customer_email or customer_firstname or customer_lastname):
        return page_not_found(404)

    query = query[:-2] + ')'
    cur = cnx.cursor()
    #cur.execute(query, to_filter)
    #data = [dict((cur.description[idx][0], value) 
    #            for idx, value in enumerate(row)) for row in cur.fetchall()]
    #return jsonify(data)
    return str(query)


  #  http://127.0.0.1:5000/api/customers/create?customer_firstname=Jason&customer_lastname=Semon&customer_email=jason.semon@gmail.com&customer_oauth_id=1233456789