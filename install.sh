#!/bin/bash
set -x
set -e

# install general pre-reqs


# 1, install influx, could be move to python3 code
dpkg -s docker-compose >/dev/null || sudo apt install docker-compose -y

pgrep -f dockerd >/dev/null || sudo systemctl start docker
docker image ls influxdb:1.8 |grep influxdb >/dev/null || docker pull influxdb:1.8

    # start local influxdb

cd influx
docker-compose up -d

sleep 10
    #create default localdb user, helene:helena
curl "http://localhost:8086/query" --data-urlencode \
        "q=CREATE USER helena WITH PASSWORD 'helena' WITH ALL PRIVILEGES" >/dev/null

    #create default localdb measurements
curl http://localhost:8086/query -u helena:helena --data-urlencode "q=CREATE DATABASE shake WITH DURATION 2d REPLICATION 1 SHARD DURATION 12h" >/dev/null
curl http://localhost:8086/query -u helena:helena --data-urlencode "q=CREATE DATABASE status WITH DURATION 2d REPLICATION 1 SHARD DURATION 12h" >/dev/null
curl http://localhost:8086/query -u helena:helena --data-urlencode "q=CREATE DATABASE healthresult WITH DURATION 2d REPLICATION 1 SHARD DURATION 12h" >/dev/null

# 2, install helena, could be move to python3 code

cd ..

sudo cp helena/services/influxshake.service /lib/systemd/system/
sudo cp helena/services/helena.service /lib/systemd/system/

sudo systemctl enable helena.service
sudo systemctl enable influxshake.service

if [ ! -e "/opt/helena/logs" ]; then
   mkdir /opt/helena/logs
fi

# 3, setup RaspiWiFi

if [ ! -e "/etc/raspiwifi" ]; then
   cd RaspiWiFi
   sudo python3 initial_setup.py
fi
