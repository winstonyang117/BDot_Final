#!/bin/bash

set -x
set -e

cd helena 

pyinstaller helena_app.py --clean --onefile \
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


mv dist/helena_app ./

cd ..

tar cvzf build/beddot.tar.gz  helena/helena_app \
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
                        
