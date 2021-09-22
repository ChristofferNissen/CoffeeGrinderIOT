import time
import base64
import ttn
from random import randint

import logging
logging.basicConfig(filename='/var/log/coffeebot.log', level=logging.INFO)

app_id = "coffeegrinderiot"
access_key = "ttn-account-v2.GPKtvM0_H3ntqqXrp3b-ijs53XoxdOr8i7aCDOO4d_c"
mqtt_client = ttn.HandlerClient(app_id, access_key).data()
bytes = [
         'AQEBAQ==', # 01 01 01 01
         'AgEBAQ==', # 02 01 01 01
         'AQIBAQ==', # 01 02 01 01
         'AQECAQ==', # 01 01 02 01
         'AQEBAg==', # 01 01 01 02
         'AwEBAQ==', # 03 01 01 01
         ]

# using mqtt client
while True:
  mqtt_client.connect()
  payload = bytes[randint(0, len(bytes) - 1)]
  logging.info(f"Sending{base64.b64decode(payload)}")
  mqtt_client.send("coffeegrinderdevice", payload, port=1, sched="replace")
  mqtt_client.close()
  time.sleep(60)  # every minute