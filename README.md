# BedDot Project

This is the complete guide for installing packages and running BedDot System. All these instructions work on a fresh-installation Raspberry Pi

## Setup Wifi

```
sudo nano /etc/wpa-supplicant/wpa-supplicant.conf
```
Add the follows by replacing testing and testingPassword with your wifi SSID and password

```
network={
    ssid="testing"
    psk="testingPassword"
}
```
More details are at https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md

## Check out helena repository
```
apt-get install git-core
git clone https://github.com/jclementes/helena
```

## Install the needed libraries

```
cd ~
sudo apt-get update
sudo apt-get install build-essential python-scipy python-influxdb python-nitime python-pip python-pandas
sudo pip install netifaces
sudo pip install configobj
```

The library installation script is also in helena/scripts/helena.sh

(We highly recommend to check carefully the installation for user’s inputs or running the commands directly by yourself instead the script)

### Configure the unit

```
cd ~/helena/conf/
sudo nano config.sys
```
change unitid = helena9 if your unit number is 9


If you are running the code in a Pi’s without local seismometer and local InfluxDB, you need to point out the cloud server with follows - this is just to verify the code works and will not do anything if there is no data from the unit.

Change the local ip 127.0.0.1 to our cloud server IP
[localdb]
clip   = 47.254.30.226


If you unit already has the helena service running, then stop it before running new python code
```
sudo systemctl stop helena
```

In case you want to stop/start influxshake and helena, please refer below

```
sudo systemctl stop influxshake
sudo systemctl stop helena
sudo systemctl start influxshake
sudo systemctl start helena
```

To see what service is running, enter
```
systemctl list-unit-files |grep enabled
```

influxshake.service and helena.service file needs to copied to /etc/systemd/system

More on how to create and start/stop services: https://medium.com/@benmorel/creating-a-linux-service-with-systemd-611b5c8b91d6

### Run the python code

run the python code for data storage to local and remote influxdb
```
cd ~/helena/components
sudo sh influxservice.sh
```

run the python code for data processing
```
cd ~/helena
sudo python main.py
```
Here you need to wait a few seconds to start seeing the  data

## Install python compiler

```
cd  ~
git clone https://github.com/pyinstaller/pyinstaller
cd ~/pyinstaller/bootloader
python ./waf distclean all
cd ~/pyinstaller 
sudo python setup.py install
sudo pip install PyCrypto
```

## Compile the CODE and Encrypt the Software for Release

B1. To compile the code, install the following libraries

```
cd  ~
mv helena/compiling . 
cd compiling
chmod +x pycompile.sh
sudo ./pycompile.sh ~/helena main.py
```

The executable file will be here: helena/dist

B2. Generate the key
```
~/helena/generate.sh
rm ~/helena/generate.sh
```

B3. Copy main and key to helena root directory: 

```
cd ~
cd helena/dist
cp main ../
cp key ../
```

They are under scripts/compHelena.sh


### Run the released execution file 

```
cd ~
cd helena
sudo ./main
```

## Code directory structures

```
helena 
    |- main.py #the main program for data processing and write processing result to local and remote database.
    |- algorithm.py # the data processing algorithms
    |- helenaservice.sh # call /opt/helena/main.py 
    |- detect_peaks.py # main.py use it by including "from detect_peaks import detect_peaks"
    |- components
        |- influxshake.py # this program reads sensor data from PiShake's UDP port 8888 and write to local and remote database
                          # it also writes the PiShake's IP addres to the local and remote database.
        |- influxservice.sh # call /opt/helena/influxshake.py
        |- saveResult.py  # this program saves the processed result into the local and remote database; 
                          # where saveRemoteResult=true/false may be configured in conf/config.sys file
        |- systemparameter.py # it will overwrite some configuration parameters in config.sys, such as wifi ssid/password and alert email 
                                # this needs to be changed, if we agree to move email and sms functions to the cloud
    |- services # those two files need to copied to /etc/systemd/system, then start with 'sudo systemctl start xxx'
        |- helena.service # call /home/myshake/helena/helenaservice.sh
        |- influxshake.service # call /home/myshake/helena/components/influxservice.sh
    |- conf
        |- config.sys # configuration files
    |- reliability # functions to clean logs and monitor device resource usages
        |- devicemonitor.py
        |- cleanlogs.py
    |- keygen
        |- genkey.sh # generate the key for authentication
    |- compiling
        |- precompile.sh # it combines auth.py and main.py with new entry starts with auth.py, 
                         # then compiles with pyinstaller and adds authentication based on a key file 
        |- auth.py # authentication code
    |- scripts
        |- helena.sh # install library dependencies
        |- compHelena.sh # compile and encryption
    |- cronjobs.txt # cron jobs of BedDot programs

```

