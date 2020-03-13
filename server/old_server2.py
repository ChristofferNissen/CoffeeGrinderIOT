import time
import ttn

app_id = "coffeegrinderiot"
access_key = "ttn-account-v2.w7h8rh58UWJYy6t_dyzD_HZyW1MOGHgdFTJhJ93xwkk"

def uplink_callback(msg, client):
  print("Received uplink from ", msg.dev_id)
  print(msg)

handler = ttn.HandlerClient(app_id, access_key)

# using mqtt client
mqtt_client = handler.data()
mqtt_client.set_uplink_callback(uplink_callback)
mqtt_client.connect()
print("sending")
mqtt_client.send(dev_id="70B3D5499FAEA875",  pay="AQ==", port=1, conf=False, sched="replace")
# time.sleep(60)
mqtt_client.close()


# using application manager client
app_client =  handler.application()
my_app = app_client.get()
print(my_app)
my_devices = app_client.devices()
print(my_devices)
