# See https://docs.pycom.io for more information regarding library specifics

from pytrack import Pytrack
from L76GNSS import L76GNSS
from LIS2HH12 import LIS2HH12

py = Pytrack()
l76 = L76GNSS(py, timeout = 60) # GSP timeout set to 60 seconds
li = LIS2HH12(py)

print("Hello, World!")

print(li.acceleration())
print(li.roll())
print(li.pitch())
print(li.yaw())

# print(l76.coordinates())

print("Should have printed information")