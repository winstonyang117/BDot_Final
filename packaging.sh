#!/bin/bash

set -x
set -e

cd helena 

pyinstaller componets/influxshake.py --clean --onefile
pyinstaller componets/systemParameters.py --clean --onefile
pyinstaller reliability/deviceMonitor.py --clean --onefile

pyinstaller main.py --clean --onefile \
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
                --hidden-import=statsmodels.tsa.statespace._smoothers._univariate_diffuse

if [ ! -e "bin" ]; then
   mkdir bin
fi

mv dist/* bin/

cd ..

tar cvzf build/beddot.tar.gz  helena/bin \
                        helena/componets/influxservice.sh      \
                        helena/componets/restartProcess.sh     \
                        helena/componets/updateParameters.sh   \
                        helena/conf                            \
                        helena/reliability/cleanlogs.sh        \
                        helena/reliability/saveMonitorStatus.sh \
                        helena/services    \
                        helena/helenaservice.sh \
                        influx      \
                        RaspiWiFi   \
                        install.sh
                        
