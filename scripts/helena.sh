#!/bin/bash
cd ~
sudo apt-get update
sudo apt-get install build-essential 

pip3 uninstall numpy  # remove previously installed version
apt install python3-numpy
pip3 uninstall scipy  # remove previously installed version
apt install python3-scipy

sudo pip3 install influxdb nitime pandas netifaces configobj

