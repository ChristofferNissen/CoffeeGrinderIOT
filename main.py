#!/usr/bin/env python
#
# Copyright (c) 2020, Pycom Limited.
#
# This software is licensed under the GNU GPL version 3 or any
# later version, with permitted additional terms. For more information
# see the Pycom Licence v1.0 document supplied with this file, or
# available at https://www.pycom.io/opensource/licensing
#

# from L76GNSS import L76GNSS # old acclerator lib
import machine
import math
import network
import os
import time
import utime
import gc
import math
import pycom
from machine import RTC
from machine import SD
from LIS2HH12 import LIS2HH12
from pytrack import Pytrack
from L76GLNSV4 import L76GNSS



# setup as a station
wlan = network.WLAN(mode=network.WLAN.STA)
wlan.connect('CN - Cisco', auth=(network.WLAN.WPA2, 'stifstof1'))
while not wlan.isconnected():
    utime.sleep_ms(50)

print(wlan.ifconfig())

# gc
gc.enable()

# setup rtc
rtc = machine.RTC()
rtc.ntp_sync("pool.ntp.org")
utime.sleep_ms(750)
print('\nRTC Set from NTP to UTC:', rtc.now())
utime.timezone(3600) # 3600 = Berlin
print('Adjusted from UTC to EST timezone', utime.localtime(), '\n')


print("up")
py = Pytrack()
L76 = L76GNSS(pytrack=py, timeout=10)
L76.setAlwaysOn()
li = LIS2HH12(py)

def subtract_from_each(l, mean):
    finalList = []
    for num in l:
        finalList.append((num-mean)**2)
    return (finalList)

def standard_deviation(l, num_measurements):
    # 1. Work out the Mean (the simple average of the numbers)
    mean = sum(l)/num_measurements
    # 2. Then for each number: subtract the Mean and square the result
    l_minus_mean = subtract_from_each(l, mean)
    # 3. Then work out the mean of those squared differences.
    squared_mean = sum(l_minus_mean)/num_measurements
    # 4. Take the square root of that and we are done!
    final = math.sqrt(squared_mean)

    return final

def measurements_stdiv():
    num_measurements = 100

    one = []
    two = []
    three = []
    for x in range(num_measurements):
        (g1, g2, g3) = li.acceleration()
        one.append(g1)
        two.append(g2)
        three.append(g3)

    return (standard_deviation(one, num_measurements), standard_deviation(two, num_measurements), standard_deviation(three, num_measurements))

pycom.heartbeat(0)

while (True):
    # coord = L76.coordinates(debug = False)
    # print("mod lib: {} - {} - {}".format(coord, utime.localtime(), gc.mem_free()))

    (g1, g2, g3) = measurements_stdiv()

    vibrate = ((g1 > 0.01) or (g2 > 0.01) or (g3 > 0.01))
    if vibrate:
        pycom.rgbled(0x000f00)
    else:
        pycom.rgbled(0x0f0000)

    # print((g1,g2,g3))

    # print(g1)
    # print(g2)
    # print(g3)
    # gc.collect()
    # time.sleep(2)


    # print("put lopy to deepsleep for 1 second ")
    # machine.deepsleep(1000)

    # example using the deepsleep mode of the pytrack
    # machine.idle()
    # py.setup_sleep(60) # sleep 1 minute
    # py.go_to_sleep(gps=True)

