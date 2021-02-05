# 1. BedDot Development Quick Start 
This is a quick start guide for **developers** to setup development enviroment and work on the BedDot system, assuming target is Raspberry Pi (3B) with raspberryshake image v18 installed.

For more details, See [here](docs/DevelopmentStart.md)

## 1.1 Clone BedDot repository
```
cd ~
apt-get install git-core
git clone https://github.com/wsonguga/BedDotV3.git 
```
The repo is cloned to ~/BedDotV3 directory, which will be the top working directory. 

## 1.2 Install prerequesites
```
cd ~/BedDotV3/helena/scripts
./helena.sh
```
This may take a while. In particular, statsmodels package take a long time.

To install pytorch on Raspberry Pi, follow https://github.com/Paratra/torch160_vision070_armv7 to use pip3 install.

```
pip3 install torch-1.6.0a0+b31f58d-cp37-cp37m-linux_armv7l.whl 
pip3 install torchvision-0.7.0a0+78ed10c-cp37-cp37m-linux_armv7l.wh
```

Note: if you want to run them as a service in Raspberry Pi, then use ```sudo pip3 install xxxx```


Now you can work on the python coding.

## 1.3 Build binaries
```
cd ~/BedDotV3
./packaging.sh
```
A tar file, beddot.tar.gz, is generated which includes the RaspiWiFi files and influxdb docker-compose file.

## 1.4 Run BedDot application
```
cd ~/BedDotV3
mv beddot.tar.gz /opt/
cd /opt
tar -xf beddot.tar.gz
./install.sh
```
The installation program will ask the information for setting up the WiFi AP mode. For development, this can be skipped by answering 'N' to the question: "Are you ready to commit changes to the system? [y/N]: "

Now the BedDot application should start running.

# 2. Deployment Guide
There are two way to prepare a ready-to-go microSD card for deployment:

## 2.1 Binary image reparation
- Download the raspishake-release.zip from raspberryShake. The current version is V18.  
```
wget https://gitlab.com/raspberryShake-public/raspshake-sd-img/-/blob/master/raspishake-release.zip
```
- Follow instructions from [here](https://gitlab.com/raspberryShake-public/raspshake-sd-img/-/tree/master) to extract the zip file to a properly formated (FAT32) microSD card. Assume you have formatted the SD card with name BEDDOT with DiskUtilities in Mac OS, then run the following command to extract zip file to SD card:
```
unzip raspishake-release.zip /Volumes/BEDDOT
```
- Insert the SD card to the device and power up. 
- Enable the network access by either plugin Ethernet cable or configure wifi by raspi-config.
- SCP the tar file to the /opt/ folder and ssh to the target.
```
cd /opt
tar -xvf beddot.tar.gz
./install.sh
```
- answer a few questions regarding wifi AP setup.
- commit the changes and allow the device to reboot. The microSD after the reboot is in WiFi AP mode, and is ready to go.

## 2.2 Disk image duplicates

- take the microSD card from previous steps.
- follow instructions [here](https://magpi.raspberrypi.org/articles/back-up-raspberry-pi) to create the SD card image.
- burn the image to other microSD card (FAT32 formated).

