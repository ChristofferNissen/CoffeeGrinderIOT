FROM python:3.8.2-slim-buster
EXPOSE 1883
EXPOSE 5000

RUN mkdir /mqttserver

COPY requirements.txt /mqttserver/

WORKDIR /mqttserver

RUN pip install -r requirements.txt

COPY mqttinterceptor.py /mqttserver/

CMD ["python", "-u" ,"mqttinterceptor.py"]
