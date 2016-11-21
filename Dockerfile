FROM resin/armv7hf-debian:jessie
MAINTAINER Ash

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    logrotate \
    cron \
    gcc \
    gpsd \
    gpsd-clients \
    kmod \
    lshw \
    libfftw3-double3 \
    librtlsdr0 \
    libusb-1.0-0 \
    libc6 \
    libstdc++6 \
    libgcc1 \
    libudev1 \
    python \
    python-gps \
    python-pip \
    python-dev && \
    apt-get clean && \
    apt-get -y autoclean && \
    apt-get -y autoremove && \
    rm -rf /var/lib/apt/lists/*

# Place Kalibrate
COPY binaries/kal-linux-arm /usr/local/bin/

# Place Filebeat
COPY binaries/filebeat-linux-arm /usr/local/bin
ADD https://raw.githubusercontent.com/elastic/beats/master/LICENSE /filebeat-lic

# Get Kalibrate source for posterity
ADD https://github.com/hainn8x/kalibrate-rtl/archive/master.zip /app/source


# Place the Logstash init script
# COPY init/logstash-forwarder /etc/init.d/

# Place config templates
RUN mkdir -p /etc/templates
COPY configs/filebeat.json /etc/templates

# Get the scripts in place
COPY sitch/ /app/sitch

WORKDIR /app/sitch

RUN pip install virtualenv && \
    cd /app/sitch && \
    virtualenv venv && \
    . ./venv/bin/activate && \
    pip install \
    pyserial \
    pyyaml \
    gps3 \
    hvac \
    kalibrate \
    haversine \
    python-geoip \
    python-geoip-geolite2 \
    pyudev \
    LatLon

CMD /app/sitch/venv/bin/python ./runner.py 2>&1
