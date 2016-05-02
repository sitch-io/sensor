FROM ioft/armhf-ubuntu:15.04
MAINTAINER Ash

RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    cron \
    lshw \
    libfftw3-double3 \
    librtlsdr0 \
    libusb-1.0-0 \
    libc6 \
    libstdc++6 \
    libgcc1 \
    libudev1 \
    logrotate \
    python \
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
    virtualenv --clear . && \
#    pip install requests && \
#    pip install pyserial && \
#    pip install hvac && \
#    pip install kalibrate

CMD /usr/bin/python /app/sitch/runner.py
