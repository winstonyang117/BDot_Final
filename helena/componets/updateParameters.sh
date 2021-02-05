#!/bin/bash
systemctl is-active --quiet influxshake && echo "influxshake is live" || (echo "influxshake is dead" && sudo systemctl restart influxshake)
systemctl is-active --quiet helena && echo "helena is live" || (echo "helena is dead" && sudo systemctl restart helena)

cd /opt/helena/
./bin/systemParameters

echo "updateParameters.sh is called at $(date)" > /opt/log/updateParameters.log  
