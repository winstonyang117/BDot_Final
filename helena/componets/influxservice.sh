#!/bin/bash

cd /opt/helena/
./bin/systemParameters

#sudo ifup wlan0 2>/dev/null
#sleep 5

sleep 5
cd /opt/helena/
./bin/influxshake
