#!/bin/bash

set -x
set -e

cd helena 

pyinstaller helena_app.py --onefile --add-data "conf:conf"

mv dist/helena_app ../

cd ..

tar cvzf beddot.tar.gz  helena_app \
                        helena/componets/influxservice.sh      \
                        helena/componets/restartProcess.sh     \
                        helena/componets/updateParameters.sh   \
                        helena/reliability/cleanlogs.sh        \
                        helena/reliability/saveMonitorStatus.sh \
                        helena/services    \
                        helena/helenaservice.sh \
                        influx      \
                        RaspiWiFi   \
                        install.sh
                        
