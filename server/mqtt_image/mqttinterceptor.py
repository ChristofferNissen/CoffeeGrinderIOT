import json
import base64
import paho.mqtt.client as mqtt
import time
import datetime

from prometheus_client import Counter, Gauge, Histogram
from prometheus_client import generate_latest
import psutil

from flask import Flask
from flask import Response
from waitress import serve


# PROMETHEUS
CPU_GAUGE = Gauge(
    "coffeeserver_cpu_load_percent", "Current load of the CPU in percent."
)
HEARTBEAT_GAUGE = Gauge(
    "coffeeserver_last_communication", "Timestamp indicating last recieved message"
)
REPONSE_COUNTER = Counter(
    "coffeeserver_http_responses_total", "The count of HTTP responses sent."
)
REQ_DURATION_SUMMARY = Histogram(
    "coffeeserver_request_duration_milliseconds", "Request duration distribution."
)

app = Flask(__name__)

# Add /metrics route for Prometheus to scrape
@app.route("/metrics/")
def metrics():
    return Response(
        generate_latest(), mimetype="text/plain; version=0.0.4; charset=utf-8"
    )

@app.before_request
def before_request():
    # record system info before prometheus pull
    CPU_GAUGE.set(psutil.cpu_percent())


# DATABASE
import mysql.connector as mysql

#DB_HOST = "127.0.0.1" # local
DB_HOST = "172.100.18.3" # compose
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = "root"
DB_NAME = "coffee_database"

def connect_db():
    """Returns a new connection to the database."""

    # connect to mysqldb and return connection
    return mysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        passwd=DB_PASSWORD,
        database=DB_NAME,
        charset='utf8',
    )

def execute_query_no_result(query, db):
    """Executes a query in datebase and discard result"""
    cur = db.cursor(dictionary=True, buffered=True)
    cur.execute(query)
    db.commit()

def execute_query(query, db, one=False):
    """Executes a query in datebase and returns either one or all rows"""
    cur = db.cursor(dictionary=True, buffered=True)
    cur.execute(query)
    db.commit()

    # fetch all results as rows in a list of dictionaries
    rv = cur.fetchall()

    # return either the first row or all rows
    return (rv[0] if rv else None) if one else rv

def get_grinds_in_db(db):
    """Queries and prints all rows from Grinds table"""
    query = """SELECT * FROM Grinds
        ORDER BY Grinds.Duration ASC LIMIT {}""".format(10)
    grinds = execute_query(query, db)

    for msg in grinds:
        filtered_msg = {}
        filtered_msg['Id'] = msg['Id']
        filtered_msg['GrindName'] = msg['GrindName']
        filtered_msg['Duration'] = msg['Duration']
        print(filtered_msg)

def get_records_in_db():
    """Queries and prints all rows from Records table"""
    db = connect_db()
    query = """SELECT * FROM Records
        LIMIT {}""".format(10)
    grinds = execute_query(query, db)

    for msg in grinds:
        filtered_msg = {}
        filtered_msg['Id'] = msg['Id']
        filtered_msg['Grind'] = msg['Grind']
        filtered_msg['Date'] = msg['Date']
        filtered_msg['Count'] = msg['Count']
        print(filtered_msg)

    db.close()

def create_grindtypes_in_db():
    """Makes sure our GrindTypes are defined in database"""
    db = connect_db()
    existing_entries_count = execute_query("SELECT COUNT(*) FROM Grinds", db)

    print("Types of Grinds registered:", existing_entries_count[0]['COUNT(*)'])

    if not existing_entries_count[0]['COUNT(*)'] > 0:
        print("Creating initial grind types in database...")

        mocca_query = """INSERT INTO Grinds (GrindName, Duration)
                   VALUES ('{}', '{}')""".format(
                       "mocca", 19.5)

        small_query = """INSERT INTO Grinds (GrindName, Duration)
                   VALUES ('{}', '{}')""".format(
                       "small", 32)

        large_query = """INSERT INTO Grinds (GrindName, Duration)
                   VALUES ('{}', '{}')""".format(
                       "large", 40)              

        fail_query = """INSERT INTO Grinds (GrindName, Duration)
                VALUES ('{}', '{}')""".format(
                    "fail", 0) 

                                                 # Id 
        execute_query_no_result(mocca_query, db) # 1
        execute_query_no_result(small_query, db) # 2
        execute_query_no_result(large_query, db) # 3
        execute_query_no_result(fail_query, db)  # 4

    else: 
        get_grinds_in_db(db)

    db.close()

def update_db(db, grind, number):
    """Updates database by added number to existing row or create new if first of the day"""
    # check if entry for today exists
    today = datetime.date.today()
    # print(today)

    query = """SELECT COUNT(*) FROM Records WHERE Records.Date = '{}' AND Records.Grind = '{}' """.format(
                        today, grind)
    first_of_the_day = execute_query(query, db)[0]['COUNT(*)'] == 0

    # print("First of the day? ", first_of_the_day)

    if first_of_the_day: 
        query = """INSERT INTO Records (Date, Grind, Count)
                    VALUES ('{}', '{}', '{}')""".format(
                        today, grind, number)
        execute_query_no_result(query, db)
    else: 
        s_query = """SELECT Records.Count FROM Records WHERE Records.Date = '{}' AND Records.Grind = '{}'""".format(today, grind)
        current_count = execute_query(s_query, db)[0]['Count']

        u_query = """UPDATE Records SET Records.Count = {} WHERE Records.Date = '{}' AND Records.Grind = '{}'""".format(current_count + number, today, grind)
        execute_query_no_result(u_query, db)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    """MQTT Callback when connection is established"""
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")
    client.subscribe('+/devices/+/up')
    client.subscribe('+/devices/#')
    # client.subscribe('my/topic')


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    """MQTT Callback when message is recieved"""
    CPU_GAUGE.set(psutil.cpu_percent())
    start_time = time.time()

    m_in=json.loads(msg.payload)
    db = connect_db()
    # https://stackoverflow.com/questions/42731998/how-to-publish-json-data-on-mqtt-broker-in-python
    payload = m_in['payload_raw']
    bts = base64.b64decode(payload)

    seconds = time.time().__add__(1) # add one hour
    HEARTBEAT_GAUGE.set(round(seconds))
    local_time = time.ctime(seconds)
    print("New Message intercepted:", local_time)
    print("Failure", bts[3])
    print("Mocca:", bts[0])
    print("Small:", bts[1])
    print("Large:", bts[2])

    print("Updating the database")
    if bts[0] > 0: 
        update_db(db, 1, bts[0])
    if bts[1] > 0: 
        update_db(db, 2, bts[1])
    if bts[2] > 0: 
        update_db(db, 3, bts[2])
    if bts[3] > 0: 
        update_db(db, 4, bts[3])

    REPONSE_COUNTER.inc()
    t_elapsed_ms = (time.time() - start_time) * 1000
    REQ_DURATION_SUMMARY.observe(t_elapsed_ms)

    print("Database update done")

    db.close()
    


# main
print("Waiting for db container to be ready. Sleeping for 20 seconds")
time.sleep(20)

print("Setting up db..")
create_grindtypes_in_db()
get_records_in_db()
print("db ready")

print("Setting up MQTT")
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set("coffeegrinderiot", "ttn-account-v2.w7h8rh58UWJYy6t_dyzD_HZyW1MOGHgdFTJhJ93xwkk")
client.connect("eu.thethings.network", 1883, 60)

print("MQTT ready")

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
# client.loop_forever()

client.loop_start()

@app.route("/")
def main():
    return "Welcome1"

# start webserer for prometheus
if __name__ == "__main__":
   serve(app, port=5000)

# while True: 
#     continue

