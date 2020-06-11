
# 1. BedDot Development Details

The document is the **developers'**  guide to work on the BedDot system. Readers are assumed already setup the target system by following the [quick start guide.](../README.md)

## 1.1 Directory/File structure

The top working directory is ~/BedDotV3 for development. For production, the top directory is /opt.

```
├── BedDotV3            # top working directory
│   ├── beddot.tar.gz
│   ├── changedate.txt
│   ├── docs
│   │   ├── DevelopmentStart.md
│   │   ├── influxdb-grafana.md
│   │   └── RaspiWiFi.md
│   ├── helena              # directory for all helena/influxshake files
│   │   ├── algorithm.py
│   │   ├── componets
│   │   │   ├── config.py
│   │   │   ├── crypto.py
│   │   │   ├── fTime.py
│   │   │   ├── influxservice.sh     # called from influxshake.service
│   │   │   ├── influxshake.py       # entry to influxshake logic
│   │   │   ├── license.py
│   │   │   ├── logs
│   │   │   ├── restartProcess.sh
│   │   │   ├── saveResults.py
│   │   │   ├── ssidname.py
│   │   │   ├── systemParameters.py
│   │   │   └── updateParameters.sh
│   │   ├── conf
│   │   │   ├── config.sec
│   │   │   └── config.sys
│   │   ├── helena_app          # Generated/compiled single binary, NOT in repository
│   │   ├── helena_app.py       # Entry point to ALL beddot application logic
│   │   ├── helenaservice.sh    # called from helena.service
│   │   ├── main.py             # entry to helena logic
│   │   ├── reliability
│   │   │   ├── cleanlogs.sh
│   │   │   ├── deviceMonitor.py
│   │   │   ├── diskSpace.py
│   │   │   └── saveMonitorStatus.sh
│   │   ├── scripts
│   │   │   ├── compHelena.sh
│   │   │   └── helena.sh       # script to install prerequisites
│   │   ├── services            # standard service files for systemd
│   │   │   ├── helena.service
│   │   │   └── influxshake.service
│   │   ├── test.py
│   │   └── timet.py
│   ├── influx            # self-contained directory for docker containers
│   │   ├── docker-compose-server.yml
│   │   ├── docker-compose.yml
│   │   └── influxdb
│   │       ├── influxdb.conf
│   │       └── ssl
│   ├── install.sh      # installation script for deployment
│   ├── packaging.sh    # pyinstaller compile and tar ball packaging
│   ├── RaspiWiFi       # self-contained directory for RaspiWiFi setup files
│   │   ├── COPYING
│   │   ├── gpl.txt
│   │   ├── initial_setup.py
│   │   ├── libs
│   │   │   ├── configuration_app
│   │   │   ├── reset_device
│   │   │   └── uninstall.py
│   │   ├── Readme.txt
│   │   └── setup_lib.py
│   └── README.md
```

## 1.2 Work on RaspiWifi

The python code for RaspiWifi is self-contained and not dependent on any other components of the BedDot system.

See document [here](docs/RaspiWiFi.md)

## 1.3 Setup influxdb and grafana
See document [here](docs/influxdb-grafana.md)

*Note that the current selected version is inluxdb:1.8. The lates version 2.0 has changed significantly, be careful if ever  upgrade of influxdb is being considered.*

## 1.4 Configure the unit

- helena/conf/config.sys

The attributes could be left with default value.
See the default values in file [config.sys](helena/conf/config.sys).


- helena/conf/config.sec
The default local and remote database info such as IP, user name and password are encrypted in helena/conf/config.sec file. The remote database info could be automatically updated by BedDot server.

*Note that the remote database info could be removed in the future.*

- cron jobs
These are period jobs to check status of the device and clean up the log files to achieve the high availability (HA). The command to add job schedule for current user is `crontab -e`. Add below jobs to the schedule.  
```
   MAILTO=""
   0 7 * * * /opt/helena/reliability/cleanlogs.sh
   * * * * * /opt/helena/reliability/saveMonitorStatus.sh
   */5 * * * * /opt/helena/componets/updateParameters.sh
```
- Database structures
The influxdb database design of BedDot: select serie where location, value, timestamp
```
dbraw = shake # this database includes z (Raw data)
dbresults = healthresult # hr, rr, bedstatus, etc
dbstatus = status # hard disk, temperature, memory usgae.
```
The database names are defined in the config.sys file.

To start influxdb database on the device,
```
cd /opt/influx
docker-compose up -d
```
To initialize the local DBs,
```
    #create default localdb user, helene:helena
curl "http://localhost:8086/query" --data-urlencode \
        "q=CREATE USER helena WITH PASSWORD 'helena' WITH ALL PRIVILEGES"

    #create default localdb measurements
curl http://localhost:8086/query -u helena:helena --data-urlencode "q=CREATE DATABASE shake"
curl http://localhost:8086/query -u helena:helena --data-urlencode "q=CREATE DATABASE status"
curl http://localhost:8086/query -u helena:helena --data-urlencode "q=CREATE DATABASE healthresult"
```
Note that the default local DB access credential: `user/password = helena/helena`

## 1.5 Run helena components python code
Running helena components python code is very helpful for debug purpose. 

```
cd helena
sudo python3 main.py

cd helena/componets
sudo python3 influxshake.py

cd helena/reliability
sudo python3 systemParameters.py

cd helena/reliability
sudo python3 deviceMonitor.py
```
A better to run above python components is through the entry point python module `helena_app.py`,
```
cd helena
sudo python3 helena/helena_app.py arg
```
where value of arg could be one of following: main, influxshake, systemParameters, or deviceMonitor. Different argument will cause different component to be executed.  

Refer [helena/helena_app.py](helena/helena_app.py) for details.

The python debug tool `pdb3` (`pdb` for default python version) could also be used to step through the python code.

## 1.6 Run helena components as services
To enable the helena and influxshake as services:
```
sudo cp helena/services/influxshake.service /lib/systemd/system/
sudo cp helena/services/helena.service /lib/systemd/system/

sudo systemctl enable helena.service
sudo systemctl enable influxshake.service
```
To start/stop/restart influxshake and helena:

```
sudo systemctl start influxshake.service
sudo systemctl start helena.service
sudo systemctl start influxshake.service
sudo systemctl start helena.service
sudo systemctl stop influxshake.service
sudo systemctl stop helena.service
```
To check status of a service:
```
systemctl status influxshake.service
```

To see what service is running, enter
```
systemctl list-unit-files |grep enabled
```

## 1.7 BedDot software packaging
To pack the BedDot software into one single tar ball,
```
cd ~/BedDotV3
./packaging.sh
```
Two important files, among others, are genarated by the script: `helena/helena_app` and `beddot.tar.gz`.

The first is the binary code for the helena app. It can be invoked with different argument to run different helena components,
```
helena/helena_app arg
```
where value of arg could be one of following: main, influxshake, systemParameters, or deviceMonitor.  

The beddot.tar.gz file is a final production software to be deployed. It includes the `install.sh`, `helena/helena_app`, `influx`, `RaspiWiFi`, some config files and help scripts.