#!/bin/bash

helpFunction()
{
   echo ""
   echo "Usage: $0 mode"
   echo -e "\t mode: py or exe or gz"
   exit 1 # Exit script after printing help
}

mode=$1

# Print helpFunction in case parameters are empty
if [ -z "$mode" ]
then
   echo "The parameter [mode] has not been set!";
   helpFunction
fi

DEV="/home/myshake/BedDotV3/helena"
RUN="/opt/helena"
BLD="/home/myshake/BedDotV3/build"
# Begin script in case all parameters are correct
case "$mode" in
    "py") cp $DEV/helenaservice_py.sh $RUN/helenaservice.sh \
    && cp $DEV/componets/influxservice_py.sh $RUN/componets/influxservice.sh \
    && cp $DEV/componets/updateParameters_py.sh $RUN/componets/updateParameters.sh \
    && cp $DEV/conf/config.sys $RUN/conf/config.sys \
    && sudo systemctl restart influxshake && sudo systemctl restart helena \
    && echo "Set running mode to python files!";;
    # "exe") cp $DEV/helenaservice.sh $RUN/helenaservice.sh \
    # && cp $DEV/componets/influxservice.sh $RUN/componets/influxservice.sh \
    # && cp $DEV/componets/updateParameters.sh $RUN/componets/updateParameters.sh \
    # && sudo systemctl restart influxshake && sudo systemctl restart helena \
    # echo "Set running mode to exe files!";;
    "gz") cp $BLD/beddot.tar.gz /opt/ && sudo systemctl stop helena && sudo systemctl stop influxshake \
    && cd /opt/ && tar -xvf beddot.tar.gz && sudo systemctl start influxshake && sudo systemctl start helena
    echo "Set running mode to gz files!";;
    "exe") cp $DEV/helenaservice.sh $RUN/helenaservice.sh \
    && cp $DEV/componets/influxservice.sh $RUN/componets/influxservice.sh \
    && cp $DEV/componets/updateParameters.sh $RUN/componets/updateParameters.sh \
    && cp $DEV/conf/config.sys $RUN/conf/config.sys \
    && cp $DEV/bin/* $RUN/bin/ \
    && sudo systemctl restart influxshake && sudo systemctl restart helena \
    && echo "Set running mode to exe files!";;
    *) echo "The parameter [mode] shall be py or exe!"; helpFunction;;
esac
