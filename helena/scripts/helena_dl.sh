#!/bin/bash

# this script installs all python3 packages for vitalsigns with DL in ubuntu
set -x
set -e

# sudo apt-get update
# sudo apt upgrade -y
sudo apt install python3.7

sudo apt-get install build-essential python-dev libatlas-base-dev -y

# uninstall pip3 version of numpy/scipy and install rpi specific packages 
sudo pip3 uninstall numpy  
sudo apt install python3-numpy -y
sudo pip3 uninstall scipy  
sudo apt install python3-scipy -y
sudo pip3 uninstall pandas
sudo apt install python3-pandas -y
sudo pip3 uninstall tornado 
sudo apt install python3-tornado -y

# for config and start/stop influxdb docker container
# sudo apt install docker-compose -y

sudo pip3 install influxdb nitime netifaces # configobj psutil cryptography pyinstaller 
sudo apt install python3-statsmodels -y

sudo pip3 install scikit-learn==0.19.2

sudo pip3 install torch

sudo apt autoremove -y

