#!/bin/bash

set -x
set -e

sudo apt-get update
sudo apt upgrade
sudo apt-get install build-essential python-dev libatlas-base-dev gfortran -y

# uninstall pip3 version of numpy/scipy and install rpi specific packages 
sudo pip3 uninstall numpy  
sudo apt install python3-numpy -y
sudo pip3 uninstall scipy  
sudo apt install python3-scipy -y

# for config and start/stop influxdb docker container
sudo apt install docker-compose -y

sudo pip3 install influxdb nitime pandas netifaces configobj psutil cryptography pyinstaller 
sudo pip3 install statsmodels

