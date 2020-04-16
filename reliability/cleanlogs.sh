#!/bin/bash

cd /var/log
sudo rm -f messages.*
sudo rm -v *.gz
sudo rm -v *.1
sudo truncate -s 0 /var/log/*.log
sudo truncate -s 0 /var/log/syslog
sudo truncate -s 0 /opt/helena/*.log
sudo truncate -s 0 /opt/helena/componets/logs/*.log

#sudo find /var/log -type f -name "*.1" -delete
#sudo find /var/log -type f -name "*.gz" -delete
