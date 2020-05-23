#!/bin/bash
set -x
set -e

# install general pre-reqs


# 1, install influx, could be move to python3 code
sudo apt install docker-compose
docker pull influxdb:1.8

    # start local influxdb
cd influx
docker-compose up -d

sleep 10
    #create default localdb user, helene:helena
curl "http://localhost:8086/query" --data-urlencode \
        "q=CREATE USER helena WITH PASSWORD 'helena' WITH ALL PRIVILEGES"

    #create default localdb measurements
curl http://localhost:8086/query -u helene:helena --data-urlencode "q=CREATE DATABASE shake"
curl http://localhost:8086/query -u helene:helena --data-urlencode "q=CREATE DATABASE status"
curl http://localhost:8086/query -u helene:helena --data-urlencode "q=CREATE DATABASE healthresult"

# 2, install helena, could be move to python3 code
sudo cp helena/services/influxshake.service /lib/systemd/system/
sudo cp helena/services/helena.service /lib/systemd/system/

# 3, setup RaspiWiFi

cd RaspiWiFi
sudo python3 initial_setup.py

