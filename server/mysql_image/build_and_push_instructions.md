# Build mysql docker image

In folder mysql_image

Build the image by 

``` bash
docker build . -t stifstof/coffeesql:latest
```

Push the image by

``` bash
docker push stifstof/coffeesql:latest
```

Optionally, run the image by 

``` bash
docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=root stifstof/coffeesql:latest 
```
