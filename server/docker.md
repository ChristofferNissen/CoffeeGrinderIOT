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

or 

when containers are still up and running

```bash
docker ps
```

will output something similar to this, but different:

``` bash
➜  mqtt_image git:(master) ✗ docker ps
CONTAINER ID        IMAGE                              COMMAND                  CREATED              STATUS              PORTS                                        NAMES
caa0a9a9e707        stifstof/coffeemqttserver:latest   "python -u mqttinter…"   About a minute ago   Up About a minute   0.0.0.0:80->80/tcp, 0.0.0.0:1883->1883/tcp   mqttcontainer
0b05d94b7c71        stifstof/coffeesql:latest          "docker-entrypoint.s…"   3 minutes ago        Up About a minute   0.0.0.0:3306->3306/tcp, 33060/tcp            coffeesqlcontainer
```

Here you see that coffeesql have container id: 0b05d94b7c71

then run

``` bash
docker inspect 0b05d94b7c71
```

outputs (alot). Somewhere near the bottom you see (under Networks):

``` bash
                    "Gateway": "172.19.0.1",
                    "IPAddress": "172.19.0.2",
                    "IPPrefixLen": 16,
                    "IPv6Gateway": "",
```

Open ./server/mqttinterceptor.py and change the ip to the ip output from docker inspect on line 12

Then build the image by 

``` bash
docker build . -t stifstof/coffeemqttserver:latest
```

Try again

``` bash
docker-compose up
```