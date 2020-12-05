# Cite from https://diode.io/raspberry%20pi/running-forever-with-the-raspberry-pi-hardware-watchdog-20202/
# sudo apt-get update
if [ ! -f "/etc/watchdog.conf" ]; then
 sudo apt-get install watchdog -y
 echo 'dtparam=watchdog=on' | sudo tee -a /boot/config.txt
 echo 'watchdog-device = /dev/watchdog' | sudo tee -a /etc/watchdog.conf
 echo 'watchdog-timeout = 15' | sudo tee -a /etc/watchdog.conf
 echo 'max-load-1 = 24' | sudo tee -a /etc/watchdog.conf
 # echo 'interface = wlan0' >> /etc/watchdog.conf # enable this will cause RaspWifi does not fall back to AP mode
fi

sudo systemctl enable watchdog
sudo systemctl start watchdog
# sudo systemctl status watchdog
