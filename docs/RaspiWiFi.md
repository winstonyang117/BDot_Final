# Wifi Setup on BetDot

Instructions on installation and configuration of WiFi on BetDot based off a forked version of open source software [RaspiWiFi](https://github.com/jasbur/RaspiWiFi)

**AP (Host) Mode** - device serves as WiFi Access Point to which other wifi-enabled devices (in client mode) can connect.

**Client Mode** - device in normal operation mode will be able to connect to a WiFi AP.

##  Installation
On Github repository, RaspiWiFi software is located at `BedDot->RaspiWiFi` directory.

- Copy RaspiWiFi to `/opt/RaspiWiFi` directory
- cd `/opt/RaspiWiFi `
- `sudo python3 initial_setup.py`


You will be prompted to set a few variables:

```
--- "SSID Prefix" [default: "RaspiWiFi Setup"]: This is the prefix of the SSID. The last four digits of device's serial number
will be appended to whatever you enter here.

--- "Auto-Config mode" [default: n]: If you choose to enable this mode your Pi will check for active WiFi connection while in normal operation mode (Client Mode). If an active connection has been determined to be lost, the Pi will reboot back into AP automatically.

--- "Auto-Config delay" [default: 300 seconds]: This is the time in consecutive seconds to wait with an inactive connection before triggering a reset into AP mode. This is only applicable if the "Auto-Config mode" mentioned above is enabled.

--- "Server port" [default: 12345]: This is the server port that the web server hosting the Configuration App page will be listening on. You would navigate to: http://10.0.0.1:12345 to complete the WiFi client settings.
```
All the settings and required software are installed at `/etc/raspiwifi` directory. After completion of installation, the device will be rebooted to WiFi **AP (Host) Mode**. 

> Everything in `/opt/RaspiWiFi` can now be deleted.

##  Wifi Client Mode configuration
On a WiFi-enabled device, navigate to http://10.0.0.1:12345 web page. Select the SSID of the WiFi AP, input the corresponding passphrase, and click on the commit button.

This will cause the device reboot to the client mode, the normal operational mode.

When device comes out of reboot, it should be able to connect to Internet.

If auto-config is enabled, and the device is not able to establish wifi connection for preconfigured time, it will reboot to AP mode again and user can reconfigure the SSID and passphrase information.

##  Manual rescue
If auto-config is NOT enabled, and the device is not able to establish wifi connection. User can manually reset the device to AP mode by following command:

`sudo python3 /usr/lib/raspiwifi/reset_device/manual_reset.py`

##  References
- Open source software: [RaspiWiFi](https://github.com/jasbur/RaspiWiFi)

- Official Raspberry PI documentaion on wireless CLI: [here](
https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md)

