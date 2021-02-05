#!/bin/bash

# cd /opt/helena/
#sudo ifup wlan0 2>/dev/null
#sleep 5
# ./bin/influxshake

cd /home/myshake/BedDotV3/helena/componets
python3 systemParameters.py
sleep 5

cd /home/myshake/BedDotV3/helena/componets
python3 influxshake.py
