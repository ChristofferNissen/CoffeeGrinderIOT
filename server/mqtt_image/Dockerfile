FROM python:3.8.2-slim-buster

RUN mkdir /mqttserver

COPY mqttinterceptor.py /mqttserver/
COPY requirements.txt /mqttserver/

WORKDIR /mqttserver

RUN pip install -r requirements.txt

EXPOSE 1883

ENTRYPOINT ["python", "mqttinterceptor.py"]
