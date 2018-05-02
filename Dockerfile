FROM resin/armv7hf-debian:jessie
MAINTAINER http://sitch.io

ENV FEED_RADIO_TARGETS="GSM"
ENV GSM_MODEM_BAND="ALL_BAND"
ENV KAL_BAND="GSM850"
ENV KAL_GAIN="60"
ENV KAL_THRESHOLD="1000000"
ENV FEED_URL_BASE="https://github.com/sitch-io/sensor_feed/raw/master/feed/"
ENV MCC_LIST="310,311,312,316"

ENV MODE="full"

COPY apt-install /

RUN apt-get update && apt-get install -y --no-install-recommends \
    `cat /apt-install` && \
    apt-get clean && \
    apt-get -y autoclean && \
    apt-get -y autoremove && \
    rm -rf /var/lib/apt/lists/*

# Place Kalibrate
COPY binaries/kal-linux-arm /usr/local/bin/

# Place Filebeat
COPY binaries/filebeat-linux-arm /usr/local/bin

# Place config templates
RUN mkdir -p /etc/templates
COPY configs/filebeat.json /etc/templates

# Place schema file
RUN mkdir /etc/schemas
COPY configs/feed_db_translation.yaml /etc/schemas
COPY configs/feed_db_schema.yaml /etc/schemas


# Get the scripts in place
COPY sitch/ /app/sitch

COPY requirements.txt /requirements.txt

WORKDIR /app/sitch

RUN pip install virtualenv==15.1.0 && \
    virtualenv venv && \
    . ./venv/bin/activate && \
    pip install -r /requirements.txt

CMD unbuffer /app/sitch/venv/bin/python ./runner.py 2>&1 | tee -a /data/sitch/log/console.log /dev/tty1
