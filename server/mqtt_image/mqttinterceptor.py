import json
import base64
import paho.mqtt.client as mqtt
import time
import datetime

#  from mysql import connector as conn
import mysql.connector as mysql

# TODO change...
# mysqldb connection
# DB_HOST = "mt_mysql"

#DB_HOST = "127.0.0.1" # local
DB_HOST = "172.18.0.2" # compose
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
    cur = db.cursor(dictionary=True, buffered=True)
    cur.execute(query)
    db.commit()

def execute_query(query, db, one=False):
    cur = db.cursor(dictionary=True, buffered=True)
    cur.execute(query)
    db.commit()

    # fetch all results as rows in a list of dictionaries
    rv = cur.fetchall()

    # return either the first row or all rows
    return (rv[0] if rv else None) if one else rv

def get_grindtypes_in_db(db):
    # db = connect_db()
    query = """SELECT * FROM Grinds
        ORDER BY Grinds.Duration ASC LIMIT {}""".format(10)
    grinds = execute_query(query, db)

    for msg in grinds:
        filtered_msg = {}
        filtered_msg['Id'] = msg['Id']
        filtered_msg['GrindName'] = msg['GrindName']
        filtered_msg['Duration'] = msg['Duration']
        print(filtered_msg)

    # db.close()

def get_records_in_db(db):
    # db = connect_db()
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

def create_grindtypes_in_db():
    db = connect_db()
    existing_entries_count = execute_query("SELECT COUNT(*) FROM Grinds", db)

    print("Count:", existing_entries_count[0]['COUNT(*)'])

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
        get_grindtypes_in_db(db)

    db.close()

def update_db(db, grind, number):
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
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")
    client.subscribe('+/devices/+/up')
    client.subscribe('+/devices/#')
    client.subscribe('my/topic')


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    m_in=json.loads(msg.payload)
    db = connect_db()
    # https://stackoverflow.com/questions/42731998/how-to-publish-json-data-on-mqtt-broker-in-python
    payload = m_in['payload_raw']
    bts = base64.b64decode(payload)

    seconds = time.time()
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
    
    print("Database update done")

    db.close()
    


# main
print("Waiting for db container to be ready. Sleeping for 30 seconds")
time.sleep(30)

db = connect_db()
print("Setting up db..")
create_grindtypes_in_db()
get_records_in_db(db)
print("db ready")
db.close()

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
client.loop_forever()
