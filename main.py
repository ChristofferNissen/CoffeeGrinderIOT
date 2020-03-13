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
from network import LoRa
import socket
import ubinascii
import binascii

# DEBUG VARIABLES
VIBRATION_LIGHT_INDICATOR = False
DEBUG = False

# Defines the different types of grinds identified by the device
class GrindDuration:
    MOCCA = 12.5 + 7
    SMALL = 25 + 7
    LARGE = 33 + 7

# remove blue blink and enable garbage collection
pycom.heartbeat(0)
gc.enable()

# setup rtc clock
RTC = machine.RTC()
RTC.ntp_sync("pool.ntp.org")
utime.sleep_ms(750)
print('\nRTC Set from NTP to UTC:', RTC.now())
utime.timezone(3600) # 3600 = Berlin
print('Adjusted from UTC to EST timezone', utime.localtime(), '\n')

# SETUP DONE

# SETUP OBJECTS
print("up")

# LORA
# Initialise LoRa in LORAWAN mode.
# Please pick the region that matches where you are using the device:
LORA = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
PY = Pytrack()
LI = LIS2HH12(PY)



# LED CONTROL
def solid_led(color):
    pycom.rgbled(color)

def solid_led_timed(seconds, color):
    pycom.rgbled(color)
    time.sleep(seconds)

def blink_led(times, color):
    for _ in range(times):
        pycom.rgbled(color)
        time.sleep(0.1)
        pycom.rgbled(0x000000) # black
        time.sleep(0.3)

def blink_error():
    for _ in range(2):
        pycom.rgbled(0x000000)
        time.sleep(0.05)
        pycom.rgbled(0xff0000) # red
        time.sleep(0.1)
    pycom.rgbled(0x000000) # black



# NETWORK
def join_wifi_network():
    # join wifi. Replace with more advanced network later
    wlan = network.WLAN(mode=network.WLAN.STA)
    wlan.connect('CN - Cisco', auth=(network.WLAN.WPA2, 'stifstof1'))
    while not wlan.isconnected():
        utime.sleep_ms(50)
    print(wlan.ifconfig())
    solid_led_timed(1.5, 0x006400)

def get_device_eui():
    #get your device's EUI
    lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
    return binascii.hexlify(lora.mac()).upper().decode('utf-8')

def join_lorawan_network():
    # step 1: Not nessesary once set up
    print('Check that you have set correct device EUI on the thethingsnetwork.org.',
      'The device EUI value:', get_device_eui())

    # step 2: Set auth credentials
    # create an OTAA authentication parameters
    app_eui = ubinascii.unhexlify('70B3D57ED002B1CF')
    app_key = ubinascii.unhexlify('A5B455945D46AF12CE0943BD2BCAFACE')

    # join a network using OTAA (Over the Air Activation)
    LORA.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

    # wait until the module has joined the network
    while not LORA.has_joined():
        blink_led(0.1, 0xffffff)
        time.sleep(2.5)
        print('Not yet joined...')

    # create a LoRa socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

    # set the LoRaWAN data rate
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
    return s




# Standard deviation calculation methods
def subtract_from_each_list_element(l, mean):
    # helper method for standard_deviation calculaton
    final_list = []
    for num in l:
        final_list.append((num-mean)**2)
    return final_list

def standard_deviation(l, num_measurements):
    # 1. Work out the Mean (the simple average of the numbers)
    mean = sum(l)/num_measurements
    # 2. Then for each number: subtract the Mean and square the result
    l_minus_mean = subtract_from_each_list_element(l, mean)
    # 3. Then work out the mean of those squared differences.
    squared_mean = sum(l_minus_mean)/num_measurements
    # 4. Take the square root of that and we are done!
    final = math.sqrt(squared_mean)
    return final

# SAMPLING
def sample_and_calculate_stdiv(num_of_samples):
    one = []
    two = []
    three = []

    if DEBUG:
        start = utime.time()

    for _ in range(num_of_samples):
        (g_1, g_2, g_3) = LI.acceleration()
        one.append(g_1)
        two.append(g_2)
        three.append(g_3)

    if DEBUG:
        end = utime.time()
    if DEBUG:
        print("Sampling took: " + str(end-start))
    if DEBUG:
        start = utime.time()

    std_tuple = (standard_deviation(one, num_of_samples), standard_deviation(two, num_of_samples), standard_deviation(three, num_of_samples))

    if DEBUG:
        end = utime.time()
    if DEBUG:
        print("Stdiv calc took: " + str(end-start))

    return std_tuple




def detect_vibration():
    vibration_sensitivity = 0.01

    # creates a 100 samples, and gets the stdiv for each axis
    if DEBUG:
        start = utime.ticks_ms()

    (g_1, g_2, g_3) = sample_and_calculate_stdiv(100)

    if DEBUG:
        end = utime.ticks_ms()

    if DEBUG:
        print("Total measurement time: " + str(end - start) + "ms")

    return ((g_1 > vibration_sensitivity) or (g_2 > vibration_sensitivity) or (g_3 > vibration_sensitivity))

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

    if DEBUG:
        print("sleeping for {0}s".format(delay))

    time.sleep(delay)

    return vibration

def measure_vibration_duration_ms():
    start = utime.ticks_ms()
    vibrating = run_detection_cycle_delayed(1.0)
    
    while vibrating:
        vibrating = detect_vibration()

    end = utime.ticks_ms()
    duration = end - start

    # log duration to sd card maybe?

    return duration




print("joining network...")
LORA_SOCKET = join_lorawan_network()

# coffee_count = ['MOCCA', 'SMALL', 'BIG', 'FAILURE']
COFFEE_COUNT = [0x00, 0x00, 0x00, 0x00]
SEND_DATA_TRIGGER = 0.0
RESET_DATA_TRIGGER = 0
DEVIATION = 2

# How often send the data count.
SEND_DATA_TIMER = 60.0 * 5 # send after 5 minutes

while True:
    DURATION = measure_vibration_duration_ms() / 1000
    SEND_DATA_TRIGGER += DURATION
    print("Duration: {0}".format(DURATION))

    if DURATION > GrindDuration.MOCCA-DEVIATION and DURATION < GrindDuration.MOCCA+DEVIATION:
        COFFEE_COUNT[0] = COFFEE_COUNT[0] + 1
        print("MOCCA detected")
        blink_led(1, 0x5a3e32)

    elif DURATION > GrindDuration.SMALL-DEVIATION and DURATION < GrindDuration.SMALL+DEVIATION:
        COFFEE_COUNT[1] = COFFEE_COUNT[1] + 1
        print("SMALL detected")
        blink_led(2, 0x5a3e32)

    elif DURATION > GrindDuration.LARGE-DEVIATION and DURATION < GrindDuration.LARGE+DEVIATION:
        COFFEE_COUNT[2] = COFFEE_COUNT[2] + 1
        print("LARGE detected")
        blink_led(3, 0x5a3e32)

    elif SEND_DATA_TRIGGER > SEND_DATA_TIMER:
        print('Sending data:', 'MOCCA:', COFFEE_COUNT[0], 'SMALL:',
              COFFEE_COUNT[1], 'BIG:', COFFEE_COUNT[2], 'FAILURE:', COFFEE_COUNT[3])
        LORA_SOCKET.send(bytes(COFFEE_COUNT))
        print('Sent successfully.')
        # reset variables
        COFFEE_COUNT = [0x00, 0x00, 0x00, 0x00]
        SEND_DATA_TRIGGER = 0

    elif DURATION < 3:
        # skip this measurement, somebody bumped machine

        # STATUS GREEN BLINK
        if DEBUG:
            blink_led(1, 0x006400)

        continue

    else:
        print("Not recognied. Container not full enough for selected grind")
        COFFEE_COUNT[3] = COFFEE_COUNT[3] + 1
        blink_error()

    if SEND_DATA_TRIGGER > SEND_DATA_TIMER:
        print('Sending data:', 'MOCCA:', COFFEE_COUNT[0], 'SMALL:', COFFEE_COUNT[1],
              'BIG:', COFFEE_COUNT[2], 'FALURE:', COFFEE_COUNT[3])
        LORA_SOCKET.send(bytes(COFFEE_COUNT))
        print('Sent successfully.')
        COFFEE_COUNT = [0x00, 0x00, 0x00, 0x00]
        SEND_DATA_TRIGGER = 0
