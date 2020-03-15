docker build mysql_image/ -t stifstof/coffeesql:latest -f mysql_image/Dockerfile
docker build grafana_image/ -t stifstof/iotgrafana:latest -f grafana_image/Dockerfile
docker build mqtt_image/ -t stifstof/coffeemqttserver:latest -f mqtt_image/Dockerfile

docker push stifstof/coffeesql:latest
docker push stifstof/iotgrafana:latest
docker push stifstof/coffeemqttserver:latest