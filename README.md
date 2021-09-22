# CoffeeGrinderIOT

This is an old uni project extended to become a Loki prototype setup. I have modified the readme to this use case. The old README.md can be found in the root as README.md.old

## Root folder
***Make sure you have the antenna connected before running the scripts, otherwise it can seriously harm the LoPy4 Lora chip***
Main.py and Boot.py are MicroPython scripts to be run on a LoPy4 development board with the PyTrack Extension Board.

The scripts connects to the LoraWAN network The Things Network via MQTT Mosquitto. 

## Server

The server consists of: 

- mysql 
    MySQL image with preloaded database schema
- mqtt 
    MQTT is a lightweight message-queue protocol used for IoT devices due to low overhead.
- grafana 
    Grafana is used for visualizing metrics and data
- loki
    Grafana Loki with Loki Canary instance. Loki ingests logs Promtail, indexes and stores the logs for querying by Grafana
- promtail
    Promtail takes logs from filesystem and passes the raw log changes to Loki for indexing and long term storage.
- prometheus
    Prometheus is used to collect metrics from services. Pull-based approach.
- alertmanager
    AlertManager is used to alert teammembers about issues identified throgh Loki or Prometheus
- bot
    The bot image is used to generate traffic, to simulate an IoT device.

All the components are included in the docker-compose file.

From within the server directory, start the server with 

```
docker-compose pull
docker-compose up
```

### Building the images

In the server directory you will find four folders for building the docker images. 

For convinience i included a script ```build_docker_images.sh```

### Docker-Compose

The server is intended to be used with ```docker-compose up``` and ```docker-compose down```

The file contains a volume for grafana and mysql, so those containers have persistent storage

### Vagrant DigitalOcean [NOT USED FOR THIS PROTOTYPE]

Due to a bug in the DigitalOcean vagrant plugin, create a docker droplet 18.04 with hostname coffeeserver manually. 
After this, the current directory (server) can be synced to the digital ocean droplet with ```vagrant provision```

## URLS 

Find Grafana Dashboard here http://localhost:3000/

*default user is and pass admin*

*Look for ```Loki Logs``` and ```Coffee Dashboad under Dashboards``` -> Manage Dashboards*

Find Prometheus instance here http://localhost:9090/

Find AlertManager instance here http://localhost:9093/

Find Promtail instance here http://localhost:8080/