# CoffeeGrinderIOT

## Root
Main.py and Boot.py are MicroPython scripts to be run on our LoPy4 development board with the PyTrack Extension Board. 

The scripts connects to the LoraWAN network The Things Network via MQTT Mosquitto. Make sure you have the antenna connected before running the scripts, otherwise it can seriously hard the LoPy4

## Server

The server consists of: 

- Python bot script in bot_image/

  This project was created for an IOT project at ITU. Due to COVID-19 we can't test our project due to people not being allowed in the cafe. We created this bot to simulate traffic from the device to showcase the grafana dashboard.

- grafana in grafana_image/

To utilize IAC we have created a docker image that preloads our data sources and dashboard.

- Python MQTT Interceptor in mqtt_image/

  To read messages from TheThingsNetwork MQTT Broker we created a Python script that parses the massages as they are sent from the device. To connect to the network, we utilize MQTT Mosquitto. 

  To allow prometheus to scrape the application, we also included a webserver 

- mysql 

MySQL image with preloaded database schema

- (DockerHub) Prometheus

  Prebuild Prometheus docker image

## Building the images

In the server directory you will find four folders for building the docker images. 

For convinience i included a script ```build_docker_images.sh```

## Docker-Compose

The server is intended to be used with ```docker-compose up``` and ```docker-compose down``

The file contains a volume for grafana and mysql, so those containers have persistent storage

## Vagrant DigitalOcean

Due to a bug in the DigitalOcean vagrant plugin, create a docker droplet 18.04 with hostname coffeeserver manually. 
After this, the current directory (server) can be synced to the digital ocean droplet with ```vagrant provision```

## Find our Live Dashboard here

http://iotcoffee.online:3000/
