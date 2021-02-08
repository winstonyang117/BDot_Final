#!/bin/bash

set -x
set -e

if [ ! -e "build" ]; then
   mkdir build
fi

date -r helena/bin/main > version.txt

# tar cvzf build/beddot.tar.gz  helena/bin \
#                         helena/componets/influxservice.sh      \
#                         helena/componets/restartProcess.sh     \
#                         helena/componets/updateParameters.sh   \
#                         helena/conf                            \
#                         helena/models                          \ 
#                         helena/reliability/cleanlogs.sh        \
#                         helena/reliability/saveMonitorStatus.sh \
#                         helena/services    \
#                         helena/helenaservice.sh \
#                         helena/cronjobs \
#                         install.sh  \
#                         update.sh  \
#                         version.txt 

# tar cvzf build/beddot.tar.gz  helena/bin \
#                         helena/componets/influxservice.sh      \
#                         helena/componets/restartProcess.sh     \
#                         helena/componets/updateParameters.sh   \
#                         helena/conf                            \
#                         helena/models                           \
#                         helena/reliability/cleanlogs.sh        \
#                         helena/reliability/saveMonitorStatus.sh \
#                         helena/services    \
#                         helena/helenaservice.sh \
#                         helena/cronjobs \
#                         influx      \
#                         RaspiWiFi   \
#                         install.sh  \
#                         update.sh  \
#                         version.txt 

# scp -i ~/homedots.pem build/beddot.tar.gz ubuntu@homedots.us:/var/www/html/bdsoftware/
# scp -i ~/homedots.pem version.txt ubuntu@homedots.us:/var/www/html/bdsoftware/rversion.txt
# scp -i ~/homedots.pem list.txt ubuntu@homedots.us:/var/www/html/bdsoftware/list.txt

declare -a iplist=("10.0.0.84" "10.0.0.212" "10.0.0.223" "10.0.0.225")

for ip in "${iplist[@]}"
do
   echo "set up: $ip"
   scp -i ~/bdot.pem beddot.tar.gz  myshake@$ip:/opt/ && ssh -i ~/bdot.pem -t myshake@$ip 'sudo systemctl stop helena && sudo systemctl stop influxshake && cd /opt/ && tar -xvf beddot.tar.gz && sudo systemctl start influxshake && sudo systemctl start helena'
   # ssh -i ~/bdot.pem -t myshake@$ip 'cd /opt/RaspiWiFi/libs/reset_device/ && sudo python3 manual_reset.py'
done