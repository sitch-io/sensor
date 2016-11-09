FROM ioft/armhf-ubuntu:16.04
MAINTAINER Ash

RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    git \
    vim \
    logrotate \
    cron \
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
    python-pip && \
    apt-get clean && \
    apt-get -y autoclean && \
    apt-get -y autoremove

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
    virtualenv --no-site-packages venv && \
    . ./venv/bin/activate && \
    pip install pyserial && \
    pip install pyyaml && \
    pip install gps3 && \
    pip install hvac && \
    pip install kalibrate && \
    pip install haversine && \
    pip install python-geoip && \
    pip install python-geoip-geolite2 && \
    pip install pyudev && \
    pip install LatLon

CMD /app/sitch/venv/bin/python ./runner.py 2>&1
