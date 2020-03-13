import json
import base64
import paho.mqtt.client as mqtt
import time

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

    # https://stackoverflow.com/questions/42731998/how-to-publish-json-data-on-mqtt-broker-in-python
    payload = m_in['payload_raw']
    bts = base64.b64decode(payload)

    seconds = time.time()
    local_time = time.ctime(seconds)
    print("New Message intercepted:", local_time)
    print("Mocca:", bts[0])
    print("Small:", bts[1])
    print("Large:", bts[2])
    print("Failure", bts[3])

    # send request over http to api to record this mqtt message



client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set("coffeegrinderiot", "ttn-account-v2.w7h8rh58UWJYy6t_dyzD_HZyW1MOGHgdFTJhJ93xwkk")

client.connect("eu.thethings.network", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()

