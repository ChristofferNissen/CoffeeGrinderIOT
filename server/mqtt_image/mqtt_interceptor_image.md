# Build mqtt interceptor docker image

In folder mqtt_image

Build the image by 

``` bash
docker build . -t stifstof/coffeemqttserver:latest
```

Push the image by

``` bash
docker push stifstof/coffeemqttserver:latest
```

Build&push

```bash
docker build . -t stifstof/coffeemqttserver:latest; docker push stifstof/coffeemqttserver:latest
```

Optionally, run the image by 

``` bash
docker run -d -p 1883:1883 stifstof/coffeemqttserver:latest 
```
