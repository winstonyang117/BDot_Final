#!/bin/bash

cd /opt/helena/
sudo ifup wlan0 2>/dev/null
sleep 5
./helena_app influxshake
