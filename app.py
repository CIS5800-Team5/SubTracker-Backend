from flask import Flask
from flask import request, jsonify
import pymysql
import os
import logging
import json, decimal
import datetime

mysql_server="subtrackerdb.mysql.database.azure.com"
sql_database="subtracker_api"
sql_user='subtracker_rwx@subtrackerdb'
sql_pass=os.environ['sql_pass']

logger = logging.getLogger(__name__)

app = Flask(__name__)

#decimal type converter
def format_converter(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.strftime('%Y-%m-%d')
    raise TypeError

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
    try:
        cnx = pymysql.connect(user=sql_user, passwd=sql_pass, host=mysql_server, database=sql_database)
        cur = cnx.cursor()
        cur.execute('''select * from services''')
        data = [dict((cur.description[idx][0], value) 
                    for idx, value in enumerate(row)) for row in cur.fetchall()]
    except:
        return str("An error occurred")
    finally:
        cnx.close()
        if not data:
            return str("No data returned")
        else:
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
    try:
        cnx = pymysql.connect(user=sql_user, passwd=sql_pass, host=mysql_server, database=sql_database)
        cur = cnx.cursor()
        cur.execute(query, to_filter)
        data = [dict((cur.description[idx][0], value) 
                    for idx, value in enumerate(row)) for row in cur.fetchall()]
    except:
        return str("An error occurred")
    finally:
        cnx.close()
        if not data:
            return str("No data returned")
        else:
            return jsonify(data)

@app.route('/api/subscriptions/all', methods=['GET'])
def get_subscriptions():
    try:
        cnx = pymysql.connect(user=sql_user, passwd=sql_pass, host=mysql_server, database=sql_database)
        cur = cnx.cursor()
        cur.execute('''select * from subscriptions''')
        data = [dict((cur.description[idx][0], value) 
        for idx, value in enumerate(row)) for row in cur.fetchall()]
    except:
        return str("An error occurred")
    finally:
        cnx.close()
        if not data:
            return str("No data returned")
        else:
            return jsonify(data)

@app.route('/api/subscriptions/create', methods=['POST'])
def create_subscription():
    query_parameters = request.args
    customer_email = query_parameters.get('customer_email')
    service_name = query_parameters.get('service_name')
    subscription_cost = query_parameters.get('subscription_cost')
    subscription_renewal = query_parameters.get('subscription_renewal')

    if not (customer_email and service_name and subscription_cost and subscription_renewal):
        return ("Invalid request")
    else:
        query = "INSERT INTO subscriptions (customer_id, service_id, subscription_cost, subscription_renewal) VALUES ((SELECT customer_id FROM customers WHERE customer_email = '" + customer_email + "'), (SELECT service_id FROM services WHERE service_name = '" + service_name + "'), '"+ subscription_cost + "', '"+ subscription_renewal + "');"

    try:
        cnx = pymysql.connect(user=sql_user, passwd=sql_pass, host=mysql_server, database=sql_database)
        cur = cnx.cursor()
        print(cur.mogrify(query))
        cur.execute(query)
        cnx.commit()
        
    finally:
        cnx.close()
    return ""

@app.route('/api/subscriptions/delete', methods=['POST'])
def delete_subscription():
    query_parameters = request.args
    subscription_id = query_parameters.get('subscription_id')

    query = "DELETE from subscriptions where subscription_id=" + subscription_id + ";"

    if not (subscription_id):
        return ("Invalid data")

    try:
        cnx = pymysql.connect(user=sql_user, passwd=sql_pass, host=mysql_server, database=sql_database)
        cur = cnx.cursor()
        cur.execute(query)
        cnx.commit()
        return ("Deletion Successful")
    finally:
        cnx.close()

@app.route('/api/subscriptions/search', methods=['GET'])
def get_subscriptions_search():
    query_parameters = request.args

    subscription_id = query_parameters.get('subscription_id')
    customer_email = query_parameters.get('customer_email')
    service_name = query_parameters.get('service_name')

    query = "SELECT * FROM subscriptions WHERE"
    to_filter = []

    if subscription_id:
        query += ' subscription_id=%s AND'
        to_filter.append(subscription_id)
    if customer_email:
        query += ' customer_id=(SELECT customer_id from customers where customer_email = %s) AND'
        to_filter.append(customer_email)
    if service_name:
        query += ' service_id=(SELECT service_id from services where service_name = %s) AND'
        to_filter.append(service_name)

    query = query[:-3] + ';'
    logger.debug(query)
    try:
        cnx = pymysql.connect(user=sql_user, passwd=sql_pass, host=mysql_server, database=sql_database)
        cur = cnx.cursor()
        cur.execute(query, to_filter)
        data = [dict((cur.description[idx][0], value) for idx, value in enumerate(row)) for row in cur.fetchall()]
    except:
        return str("An error occurred")
    finally:
        cnx.close()
        if not data:
            return str("No data returned")
        else:
            return json.dumps(data,default=format_converter)

@app.route('/api/customers/all', methods=['GET'])
def get_customers_all():
    try:
        cnx = pymysql.connect(user=sql_user, passwd=sql_pass, host=mysql_server, database=sql_database)
        cur = cnx.cursor()
        cur.execute('''select * from customers''')
        data = [dict((cur.description[idx][0], value) 
                    for idx, value in enumerate(row)) for row in cur.fetchall()]
    finally:
        cnx.close()
        if not data:
            return str("No data returned")
        else:
            return jsonify(data)

@app.route('/api/customers/search', methods=['GET'])
def get_customers_search():
    query_parameters = request.args

    customer_id = query_parameters.get('customer_id')
    customer_email = query_parameters.get('customer_email')
    customer_phone = query_parameters.get('customer_phone')
    customer_status = query_parameters.get('customer_status')

    query = "SELECT * FROM customers WHERE"
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

    query = query[:-4] + ';'
    try:
        cnx = pymysql.connect(user=sql_user, passwd=sql_pass, host=mysql_server, database=sql_database)
        cur = cnx.cursor()
        cur.execute(query, to_filter)
        data = [dict((cur.description[idx][0], value) 
            for idx, value in enumerate(row)) for row in cur.fetchall()]
    finally:
        cnx.close()
        if not data:
            return str("No data returned")
        else:
            return jsonify(data)

@app.route('/api/customers/getsubscriptions', methods=['GET'])
def get_customer_subscriptions():
    query_parameters = request.args

    customer_email = query_parameters.get('customer_email')

    query = "SELECT customers.customer_email, services.service_name, subscriptions.subscription_cost, subscriptions.subscription_renewal FROM customers join subscriptions ON customers.customer_id = subscriptions.customer_id join services ON subscriptions.service_id = services.service_id WHERE"
    to_filter=[]

    if customer_email:
        query += ' customer_email=%s'
        to_filter.append(customer_email)

    if not (customer_email):
        return ("Invalid request")

    try:
        cnx = pymysql.connect(user=sql_user, passwd=sql_pass, host=mysql_server, database=sql_database)
        cur = cnx.cursor()
        cur.execute(query, to_filter)
        data = [dict((cur.description[idx][0], value) 
            for idx, value in enumerate(row)) for row in cur.fetchall()]
    finally:
        cnx.close()
        if not data:
            return str("No data returned")
        else:
            return json.dumps(data,default=format_converter )


@app.route('/api/customers/create', methods=['POST'])
def create_customer():
    query_parameters = request.args
    customer_email = query_parameters.get('customer_email')
    customer_phone = query_parameters.get('customer_phone')

    query = "INSERT INTO customers ("
    to_filter = []
    numvals = 0

    if customer_email:
        query += ' customer_email, '
        to_filter.append(customer_email)
        numvals += 1

    if customer_phone:
        query += ' customer_phone, '
        to_filter.append(customer_phone)
        numvals += 1

    if not (customer_email):
        return page_not_found(404)

    query = query[:-2] + ') VALUES ('
    for i in range(0, numvals):
        query = query + ' %s, '
    query = query[:-2] + ')'

    to_filter = tuple(to_filter)
    try:
        cnx = pymysql.connect(user=sql_user, passwd=sql_pass, host=mysql_server, database=sql_database)
        cur = cnx.cursor()
        cur.execute(query, to_filter)
        data = [dict((cur.description[idx][0], value) 
                    for idx, value in enumerate(row)) for row in cur.fetchall()]
        cnx.commit()
    finally:
        cnx.close()
    return ""