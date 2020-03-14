
# LORA

# create an OTAA authentication parameters
# app_eui_token = '70B3D57ED002B7ED'
# app_key_token = '8CEB6DBBF3C9E0A60DF45ED49BF1E6FB'
# app_eui = ubinascii.unhexlify(app_eui_token)
# print('App EUI was set to the value:',app_eui_token)
# app_key = ubinascii.unhexlify(app_key_token)
# print('App key was set to the value:',app_key_token)





# GPS

# to setup gps for modified api library  
# L76 = L76GNSS(pytrack=py, timeout=10)
# L76.setAlwaysOn()





# DEEP SLEEP

# print("put lopy to deepsleep for 1 second ")
# machine.deepsleep(1000)

# save this for shutting down in the night
# example using the deepsleep mode of the pytrack
# machine.idle()
# py.setup_sleep(60) # sleep 1 minute
# py.go_to_sleep(gps=True)