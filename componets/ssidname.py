import subprocess

ssid = subprocess.check_output("iwgetid -r", shell = True)
if(ord(ssid[len(ssid)-1])==10):
  ssid = ssid[0:len(ssid)-1]

print ssid

