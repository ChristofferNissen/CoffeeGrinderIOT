FROM python:3.8.2-buster
EXPOSE 1883

RUN mkdir /botserver

COPY requirements.txt /botserver/

WORKDIR /botserver

RUN pip3 install -r requirements.txt

COPY downlink_payload_bot.py /botserver/

CMD ["python", "-u" ,"downlink_payload_bot.py"]
