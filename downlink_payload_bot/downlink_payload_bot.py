import base64
import time
import ttn
import random
import string

app_id = "coffeegrinderiot"
access_key = "ttn-account-v2.GPKtvM0_H3ntqqXrp3b-ijs53XoxdOr8i7aCDOO4d_c"
letters = string.ascii_lowercase
mqtt_client = ttn.HandlerClient(app_id, access_key).data()

# using mqtt client
while True:
  mqtt_client.send("coffeegrinderdevice", base64.encodebytes(bytes(''.join(random.choice(letters) for i in range(6)), 'utf-8')).decode(), port=1, sched="replace")
  time.sleep(60000)