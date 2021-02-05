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

scp -i ~/homedots.pem build/beddot.tar.gz ubuntu@homedots.us:/var/www/html/bdsoftware/
scp -i ~/homedots.pem version.txt ubuntu@homedots.us:/var/www/html/bdsoftware/rversion.txt
scp -i ~/homedots.pem list.txt ubuntu@homedots.us:/var/www/html/bdsoftware/list.txt
