#!/bin/bash

set -x
set -e

arg=" "

if [ "$1" == "clean" ]; then
   arg="--clean"
fi

cd helena 

pyinstaller componets/influxshake.py ${arg} --onefile
pyinstaller componets/systemParameters.py ${arg} --onefile
pyinstaller reliability/deviceMonitor.py ${arg} --onefile

pyinstaller main_dl.py ${arg} --onefile \
                --hidden-import=statsmodels.tsa.statespace._kalman_initialization \
                --hidden-import=statsmodels.tsa.statespace._kalman_filter \
                --hidden-import=statsmodels.tsa.statespace._kalman_smoother \
                --hidden-import=statsmodels.tsa.statespace._representation \
                --hidden-import=statsmodels.tsa.statespace._simulation_smoother \
                --hidden-import=statsmodels.tsa.statespace._statespace  \
                --hidden-import=statsmodels.tsa.statespace._tools  \
                --hidden-import=statsmodels.tsa.statespace._filters._conventional \
                --hidden-import=statsmodels.tsa.statespace._filters._inversions \
                --hidden-import=statsmodels.tsa.statespace._filters._univariate  \
                --hidden-import=statsmodels.tsa.statespace._filters._univariate_diffuse \
                --hidden-import=statsmodels.tsa.statespace._smoothers._alternative \
                --hidden-import=statsmodels.tsa.statespace._smoothers._classical  \
                --hidden-import=statsmodels.tsa.statespace._smoothers._conventional \
                --hidden-import=statsmodels.tsa.statespace._smoothers._univariate \
                --hidden-import=statsmodels.tsa.statespace._smoothers._univariate_diffuse \
                --hidden-import=sklearn

if [ ! -e "bin" ]; then
   mkdir bin
fi

mv dist/* bin/

cd ..

if [ ! -e "build" ]; then
   mkdir build
fi

mv helena/bin/main_dl helena/bin/main

date -r helena/bin/main > version.txt

tar cvzf build/beddot.tar.gz  helena/bin/main \
                        helena/bin/influxshake \
                        helena/bin/deviceMonitor \
                        helena/bin/systemParameters \
                        helena/componets/influxservice.sh      \
                        helena/componets/restartProcess.sh     \
                        helena/componets/updateParameters.sh   \
                        helena/conf                            \
                        helena/models                           \
                        helena/reliability/cleanlogs.sh        \
                        helena/reliability/saveMonitorStatus.sh \
                        helena/services    \
                        helena/helenaservice.sh \
                        helena/cronjobs \
                        influx      \
                        RaspiWiFi   \
                        install.sh  \
                        update.sh  \
                        unpack.sh  \
                        version.txt 
                        
