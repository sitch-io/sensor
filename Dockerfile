FROM ioft/armhf-ubuntu:15.04
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


# Install Logstash
COPY packages/ /app/packages
RUN dpkg -i /app/packages/logstash-forwarder_0.4.0_armhf.deb

# Place Kalibrate
COPY binaries/kal /usr/local/bin/

# Get Kalibrate source for posterity
ADD https://github.com/hainn8x/kalibrate-rtl/archive/master.zip /app/source


# Place the Logstash init script
COPY init/logstash-forwarder /etc/init.d/

# Get the scripts in place
COPY sitch/ /app/sitch

WORKDIR /app/sitch

RUN pip install virtualenv && \
    cd /app/sitch && \
    virtualenv --no-site-packages venv && \
    . ./venv/bin/activate && \
    pip install pyserial && \
    pip install gps3 && \
    pip install hvac && \
    pip install kalibrate && \
    pip install haversine && \
    pip install python-geoip && \
    pip install python-geoip-geolite2 && \
    pip install pyudev && \
    git clone https://github.com/klynch/python-logstash-handler && \
    cd python-logstash-handler && \
    git checkout c5574624c8cb4fdba14bef33303e8650eb2f3487 && \
    pip install .

# CMD cd /app/sitch && . ./venv/bin/activate && /app/sitch/venv/bin/python ./runner.py
CMD /app/sitch/venv/bin/python ./runner.py
