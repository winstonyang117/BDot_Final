__TOC___
# BedDot development Start

The first part of this document is the start guide for **developers** to install packages and work on the BedDot system. 

The second part focuses on the **deployment** of BetDot software on a Raspberry Pi (3B) with raspberryshake image v18 installed. 


## Install prerequisites 

The prerequisited packages have changed significantly with py2 to py3 upgrade. 

See the installation script [here](helena/scripts/helena.sh)

(We highly recommend to check carefully the installation for user’s inputs or running the commands directly by yourself instead the script)

## Clone BedDot repository
```
cd ~
apt-get install git-core
git clone https://github.com/wsonguga/BedDotV3.git 
```
The repo is cloned to ~/BedDotV3 directory, which will be the top working directory. 

## Directory/File structure

The top working directory is ~/BedDotV3 for development. For production, the top directory is /opt.

```
├── BedDotV3            # top working directory
│   ├── beddot.tar.gz
│   ├── changedate.txt
│   ├── docs
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

## Setup Wifi

See document [here](docs/RaspiWiFi.md)

## Setup influxdb and grafana
See document [here](docs/influxdb-grafana.md)

*Note that the current selected version is inluxdb:1.8. The lates version 2.0 has changed significantly, be careful if ever  upgrade of influxdb is being considered.*

## Configure the unit

- helena/conf/config.sys
change unitid = < mac of eth0 >
other attributes could be left with default value
See the config.sys file [here](helena/conf/config.sys)

- helena/conf/config.sec
The default local and remote database info are encrypted in helena/conf/config.sec file. To set/or change the default setting, do:
```
cd helena/conf
python3 ../componets/utils.py -D config.sec config.tmp
```
   this will create a plaintext file config.tmp which can be modified with a text editor. After the modification, do:

```
python3 ../componets/utils.py -E config.tmp config.sec 
```
The config.sec file is the new encrypted dayabase info. 

*Note that this procedure could be automated or simplified later.* 

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
dbresults = healthresult # this database includes hr, rr, bedstatus, etc
dbstatus = status # this database collects information about the hard disk, 
                  # memory status for monitoring and reliability framework.
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

## Run helena components python code
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

## Run helena components as services
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

## BedDot software packaging
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

# Deployment preparation
There are two way to prepare a ready-to-go microSD card for deployment:

## Use tar file
- Download the raspishake-release.zip from raspberryShake. The current version is V18.  
```
wget https://gitlab.com/raspberryShake-public/raspshake-sd-img/-/blob/master/raspishake-release.zip
```
- Follow instructions from [here](https://gitlab.com/raspberryShake-public/raspshake-sd-img/-/tree/master) to extract the zip file to a properly formated (FAT32) microSD card.
- Insert the SD card to the device and power up. 
- Enable the network access by either plugin Ethernet cable or configure wifi by raspi-config.
- SCP the tar file to the /opt/ folder.
- untar the file
```
tar -xvf beddot.tar.gz
```
- Run the `install.sh`
```
cd /opt
./install.sh
```
- answer a few questions regarding wifi AP setup.
- commit the changes and allow the device to reboot. The microSD after the reboot is in WiFi AP mode, and is ready to go.

## Disk image duplicates

- take the microSD card from previous steps.
- follow instructions [here](https://magpi.raspberrypi.org/articles/back-up-raspberry-pi) to copy the SD card image.
- burn the image to other microSD card (FAT32 formated).

