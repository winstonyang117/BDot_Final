# Cite from https://diode.io/raspberry%20pi/running-forever-with-the-raspberry-pi-hardware-watchdog-20202/
#sudo apt-get update
#if [ ! -f "/etc/watchdog.conf" ]; then
sudo apt-get install watchdog
sudo su
echo 'dtparam=watchdog=on' >> /boot/config.txt
echo 'watchdog-device = /dev/watchdog' >> /etc/watchdog.conf
echo 'watchdog-timeout = 15' >> /etc/watchdog.conf
echo 'max-load-1 = 24' >> /etc/watchdog.conf
echo 'interface = wlan0' >> /etc/watchdog.conf
exit
#fi

sudo systemctl enable watchdog
sudo systemctl start watchdog
sudo systemctl status watchdog
