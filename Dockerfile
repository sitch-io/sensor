ARG ARCH=armv7hf
FROM balenalib/${ARCH}-debian-golang:1.13.12-buster as mmdb

ENV MMDB_CONFIG_FILE=/usr/local/etc/GeoIP.conf

RUN env GO111MODULE=on go get -u github.com/maxmind/geoipupdate/v4/cmd/geoipupdate

# MMDB Config
RUN echo "AccountID ${MMDB_ACCOUNT_ID:-UNSET}" > ${MMDB_CONFIG_FILE} && \
    echo "LicenseKey ${MMDB_LICENSE_KEY:-UNSET}" >> ${MMDB_CONFIG_FILE} && \
    echo "EditionIDs GeoLite2-City" >> ${MMDB_CONFIG_FILE} && \
    echo "DatabaseDirectory /var/mmdb/" >> ${MMDB_CONFIG_FILE}

RUN mkdir -p /var/mmdb/

RUN $GOPATH/bin/geoipupdate || echo "Unable to download GeoIP DB!!" && touch /var/mmdb/.placeholder

#############################################
###### Build the unit test image
FROM balenalib/${ARCH}-debian-python:3.6-jessie

# Install requirements
COPY apt-install /
RUN apt-get update && apt-get install -y --no-install-recommends \
    `cat /apt-install` \
    build-essential \
    curl \
    libffi-dev \
    libssl-dev \
    ca-certificates \
    zlib1g-dev && \
    apt-get clean && \
    apt-get -y autoclean && \
    apt-get -y autoremove && \
    rm -rf /var/lib/apt/lists/*



# Copy forward the GeoLite2 DB
COPY --from=mmdb /var/mmdb/* /var/mmdb/

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

RUN mkdir /data/

COPY requirements*.txt /

WORKDIR /app/sitch

RUN /usr/local/bin/python -m pip install virtualenv==15.1.0 && \
    virtualenv venv && \
    . ./venv/bin/activate && \
    pip install -r /requirements-test.txt && \
    py.test tests/ --cov sitchlib


##########################################
####### Build the final image
FROM balenalib/${ARCH}-debian-python:3.6-jessie

ENV FEED_RADIO_TARGETS="GSM"
ENV GSM_MODEM_BAND="ALL_BAND"
ENV KAL_BAND="GSM850"
ENV KAL_GAIN="60"
ENV KAL_THRESHOLD="1000000"
ENV FEED_URL_BASE="https://github.com/sitch-io/sensor_feed/raw/master/feed/"
ENV MCC_LIST="310,311,312,316"

ENV MODE="full"

# Install all the packages
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

# Bring forward the GeoLite2 DB
COPY --from=mmdb /var/mmdb/* /var/mmdb/

# Get the scripts in place
COPY sitch/ /app/sitch

COPY requirements.txt /requirements.txt

WORKDIR /app/sitch

RUN dpkg -l | grep gcc
RUN which gcc

RUN /usr/local/bin/python -m pip install virtualenv==15.1.0 && \
    virtualenv venv && \
    . ./venv/bin/activate && \
    pip install -r /requirements.txt

CMD unbuffer /app/sitch/venv/bin/python ./runner.py 2>&1 | tee -a /data/sitch/log/console.log /dev/tty1
