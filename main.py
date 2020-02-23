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

class GrindDuration: 
    MOCCA = 7
    SMALL = 21
    LARGE = 31

# Global debug variables
VIBRATION_LIGHT_INDICATOR = False
DEBUG = False


# SETUP START
# remove blue blink and enable garbage collection
pycom.heartbeat(0)
gc.enable()

# setup rtc clcok
rtc = machine.RTC()
rtc.ntp_sync("pool.ntp.org")
utime.sleep_ms(750)
print('\nRTC Set from NTP to UTC:', rtc.now())
utime.timezone(3600) # 3600 = Berlin
print('Adjusted from UTC to EST timezone', utime.localtime(), '\n')

# SETUP DONE

# SETUP OBJECTS
print("up")
py = Pytrack()
li = LIS2HH12(py)

# to setup gps for modified api library  
# L76 = L76GNSS(pytrack=py, timeout=10)
# L76.setAlwaysOn()


# LED CONTROL
def solid_led(color):
    pycom.rgbled(color)

def solid_led_timed(seconds, color):
    pycom.rgbled(color)
    time.sleep (seconds)

def blink_led(times, color):
    for _ in range(times):
        pycom.rgbled(color)
        time.sleep (0.1)
        pycom.rgbled(0x000000) # black
        time.sleep (0.3)

def blink_error():
    for _ in range(2):
        pycom.rgbled(0xff0000) # red
        time.sleep (0.05)
        pycom.rgbled(0xffffff) # white
        time.sleep (0.05)
    pycom.rgbled(0x000000) # black

# NETWORK
def join_network():
    # join wifi. Replace with more advanced network later
    wlan = network.WLAN(mode=network.WLAN.STA)
    wlan.connect('CN - Cisco', auth=(network.WLAN.WPA2, 'stifstof1'))
    while not wlan.isconnected():
        utime.sleep_ms(50)
    print(wlan.ifconfig())
    solid_led_timed(2, 0x00FF00)

# Standard deviation calculation methods

def subtract_from_each(l, mean):
    # helper method for standard_deviation calculaton
    finalList = []
    for num in l:
        finalList.append((num-mean)**2)
    return finalList

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

# SAMPLING

def sample_and_calculate_stdiv(samples):
    one = []
    two = []
    three = []

    if DEBUG: start = utime.time()
    for _ in range(samples):
        (g1, g2, g3) = li.acceleration()
        one.append(g1)
        two.append(g2)
        three.append(g3)
    if DEBUG: end = utime.time()
    if DEBUG: print("Sampling took: " + str(end-start))

    if DEBUG: start = utime.time()
    t = (standard_deviation(one, samples), standard_deviation(two, samples), standard_deviation(three, samples))
    if DEBUG: end = utime.time()
    if DEBUG: print("Stdiv calc took: " + str(end-start))
    return t

def detect_vibration():
    # creates a 100 samples, and gets the stdiv for each axis
    if DEBUG: start = utime.ticks_ms()
    (g1, g2, g3) = sample_and_calculate_stdiv(100)
    if DEBUG: end = utime.ticks_ms()
    if DEBUG: print("Total measurement time: " + str(end - start) + "ms")

    return ((g1 > 0.01) or (g2 > 0.01) or (g3 > 0.01)) # vibration sensitivity

def run_detection_cycle_delayed(delay):
    vibration = detect_vibration()
    
    if DEBUG:
        if VIBRATION_LIGHT_INDICATOR:
            if vibration:
                pycom.rgbled(0x000f00)
            else:
                pycom.rgbled(0x0f0000)
        else:
            print(vibration)

    print("sleeping for {0}s".format(delay))
    time.sleep(delay)

    return vibration

def measure_vibration_duration():
    start = utime.ticks_ms()
    vibrating = run_detection_cycle_delayed(1.0)
    # if vibrating: solid_led(0x006400)
    while vibrating: 
        vibrating = detect_vibration()

    end = utime.ticks_ms()
    duration = end - start

    # log duration to sd card
    # solid_led(0x000000)
    return duration

# main
join_network()
while (True):
    duration = measure_vibration_duration() / 1000
    print("Duration: {0}".format(duration))

    if duration > GrindDuration.MOCCA-1 and duration < GrindDuration.MOCCA+1:
        print("MOCCA detected")
        blink_led(1, 0x5a3e32)

    elif duration > GrindDuration.SMALL-1 and duration < GrindDuration.SMALL+1:
        print("SMALL detected")
        blink_led(2, 0x5a3e32)

    elif duration > GrindDuration.LARGE-1 and duration < GrindDuration.LARGE+1:
        print("LARGE detected")
        blink_led(3, 0x5a3e32)

    elif duration < 3:
        # skip this, somebody bumped machine
        blink_led(1, 0x006400)
        
    else: 
        # failure
        # dont show user facing error
        print("Not recognied. Container not full enough for selected grind")
        blink_error()



    # print("put lopy to deepsleep for 1 second ")
    # machine.deepsleep(1000)

    # save this for shutting down in the night
    # example using the deepsleep mode of the pytrack
    # machine.idle()
    # py.setup_sleep(60) # sleep 1 minute
    # py.go_to_sleep(gps=True)

