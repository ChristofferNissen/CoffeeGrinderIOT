# How to use our Docker Compose

Hi Peto, 

You should be able to run the MQTT server assuming you have Docker and Docker-compose installed:

in ./server run:

``` bash
docker-compose up
```

And that should be it :-)

If you make changes, you can build new images by following the directions in ./server/mqtt_image & ./server/mysql_image respectively. 




If it for some reason can't find the sql server, inspect network with:

```bash
docker network inspect server_main
```