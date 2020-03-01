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


class GrindDuration: 
    MOCCA = 7
    SMALL = 21
    LARGE = 31

# Global debug variables
VIBRATION_LIGHT_INDICATOR = False
DEBUG = False
# How often send the data count.
SEND_DATA_TIMER = 60.0
RESET_COUNTER = 86400

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

# LORA

# Initialise LoRa in LORAWAN mode.
# Please pick the region that matches where you are using the device:
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

# create an OTAA authentication parameters
app_eui_token = '70B3D57ED002B7ED'
app_key_token = '8CEB6DBBF3C9E0A60DF45ED49BF1E6FB'
app_eui = ubinascii.unhexlify(app_eui_token)
print('App EUI was set to the value:',app_eui_token)
app_key = ubinascii.unhexlify(app_key_token)
print('App key was set to the value:',app_eui_token)


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
        pycom.rgbled(0x000000)
        time.sleep (0.05) 
        pycom.rgbled(0xff0000) # red
        time.sleep (0.1)
    pycom.rgbled(0x000000) # black

# NETWORK
def join_network():
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
    # get_device_eui()

    # join a network using OTAA (Over the Air Activation)
    lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

    # wait until the module has joined the network
    while not lora.has_joined():        
        time.sleep(2.5)              
        print('Not yet joined...')

def create_socket():
    # create a LoRa socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

    # set the LoRaWAN data rate
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)

    # make the socket blocking
    # (waits for the data to be sent and for the 2 receive windows to expire)
    # s.setblocking(True)

    # send some data
    # s.send(bytes([0x01, 0x02, 0x03]))

    # make the socket non-blocking
    # (because if there's no data received it will block forever...)
    # s.setblocking(False)

    # get any data received (if any...)
    # data = s.recv(64)
    # print(data)
    return s

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


print('Check that you have set correct device EUI on the thethingsnetwork.org. The device EUI value:', get_device_eui())
print("joining network...")
# main
join_lorawan_network()
s = create_socket()
# coffee_count = ['MOCCA','SMALL', 'BIG']
coffee_count = [0x00, 0x00, 0x00]
send_data_trigger = 0.0
reset_data_trigger = 0
while (True):
    duration = measure_vibration_duration() / 1000
    print("Duration: {0}".format(duration))
    
    if duration > GrindDuration.MOCCA-1 and duration < GrindDuration.MOCCA+1:
        coffee_count[0] +=1
        print("MOCCA detected")
        blink_led(1, 0x5a3e32)

    elif duration > GrindDuration.SMALL-1 and duration < GrindDuration.SMALL+1:
        coffee_count[1] +=1
        print("SMALL detected")
        blink_led(2, 0x5a3e32)

    elif duration > GrindDuration.LARGE-1 and duration < GrindDuration.LARGE+1:
        coffee_count[2] +=1
        print("LARGE detected")
        blink_led(3, 0x5a3e32)

    send_data_trigger += duration
    if send_data_trigger > SEND_DATA_TIMER:
        print('Sending data:', 'MOCCA:', coffee_count[0],'SMALL:', coffee_count[1], 'BIG:', coffee_count[2])
        s.send(bytes(coffee_count))
        print('Sent successfully.')
        send_data_trigger = 0

    reset_data_trigger += duration
    if reset_data_trigger > RESET_COUNTER:
        print('Today was made:', 'MOCCA:', coffee_count[0],'SMALL:', coffee_count[1], 'BIG:', coffee_count[2])
        print('Reseting counter.')
        coffee_count = [0x00, 0x00, 0x00]
        reset_data_trigger = 0

    if duration < 3:
        # skip this measurement, somebody bumped machine
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

