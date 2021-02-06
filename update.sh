#!/bin/bash
mac=`cat /sys/class/net/eth0/address` # get my own MAC address
cd /opt/ && wget -N https://homedots.us/bdsoftware/list.txt 
file="/opt/list.txt"

if [ -f /opt/list.txt ] && grep -q $mac "$file"; then # update only if my MAC is in the update list
    # echo "update will start" && exit
    cd /opt/ && wget -N https://homedots.us/bdsoftware/rversion.txt && cmp --silent rversion.txt version.txt \
    || (wget -N https://homedots.us/bdsoftware/beddot.tar.gz && ./unpack.sh) \
    && echo "checked at $(date) without update" > update.log
fi
