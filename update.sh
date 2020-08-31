#!/bin/bash
set -x
set -e

sudo systemctl stop helena && sudo systemctl stop influxshake 
cd /opt/  
wget https://www.homedots.us/bdsoftware/beddot.tar.gz  
tar -xvf beddot.tar.gz && rm beddot.tar.gz && sudo reboot
