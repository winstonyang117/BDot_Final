#!/bin/bash

cd /opt/helena/componets/
sudo ifup wlan0
sleep 5
python3 influxshake.py
