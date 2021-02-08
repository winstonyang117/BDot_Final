import json
import requests
import netifaces
import subprocess
import time
import configparser
import ast
import sys, os
from configobj import ConfigObj
sys.path.insert(0, os.path.abspath('..'))

import componets.license as license
from componets.config import Config

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if getattr(sys, 'frozen', False):
   cfg_fn = r'/opt/helena/conf/config.sys'
else:
   cfg_fn = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../', 'conf/config.sys')

def parseBoolStringToInt(theString):
  if(theString[0].upper()=='T'):
    return 1 
  else:
    return 0

def parseIntToBool(theInt):
  if(theInt==1):
    return 'True' 
  else:
    return 'False'


def alarmParameters(alarmStatus,alarmType,envelopeMpd,thresholdOnBed):
   sw = 0
   config = configparser.ConfigParser()
   config.read_file(open(cfg_fn))

   enablesmson           = parseBoolStringToInt(config.get('messages', 'enablesmson'))
   enablesmsoff          = parseBoolStringToInt(config.get('messages', 'enablesmsoff'))
   enablesmsmovement     = parseBoolStringToInt(config.get('messages', 'enablesmsmovement'))
   envelopeMpdFile       = float(config.get('main', 'mpdEnv')) 
   thresholdOnBedFlie    = float(config.get('main', 'thccMean'))


   config = ConfigObj(cfg_fn)
   
   if(envelopeMpd !=None and len(envelopeMpd)>0 and float(envelopeMpd)!=envelopeMpdFile):
      sw = 1
      config['main']['mpdEnv'] = envelopeMpd
      print("Change MDP Envelope")

   if(thresholdOnBed != None and len(thresholdOnBed)>0 and float(thresholdOnBed)!= thresholdOnBedFlie):
      sw = 1
      config['main']['thccMean'] = thresholdOnBed
      print("On/Off th")

   pos = 0
   for alarmt in alarmType: 
     #onBed
     if(int(alarmt)==1):
       if(enablesmson!=int(alarmStatus[pos])):
          sw = 1
          print(parseIntToBool(int(alarmStatus[pos])))
          config['messages']['enablesmson'] = parseIntToBool(int(alarmStatus[pos])) 
#          print str(enablesmson)+"  ---  "+alarmStatus[pos]
          print("Change OnBed")

     #offBed
     if(int(alarmt)==2):
       if(enablesmsoff!=int(alarmStatus[pos])):
          sw = 1
          config['messages']['enablesmsoff'] = parseIntToBool(int(alarmStatus[pos]))
#          print str(enablesmsoff)+"  ---  "+alarmStatus[pos]
          print("Change OffBed")

     #Movement
     if(int(alarmt)==3):
       if(enablesmsmovement!=int(alarmStatus[pos])):
          sw = 1
          config['messages']['enablesmsmovement'] = parseIntToBool(int(alarmStatus[pos]))
#          print str(enablesmsmovement)+"  ---  "+alarmStatus[pos]
          print("Change Movement")

     pos = pos + 1


   if(sw==1):
     config.write()
   
   unit  = mac_address()
   return unit



def current_unitid():
   config = configparser.ConfigParser()
   config.read_file(open(cfg_fn))

   unit  = config.get('general', 'unitid')
   return unit


def mac_address():
    macEth = "gg:gg:gg:gg:gg:gg"
    data = netifaces.interfaces()
    for i in data:
      if i == 'eth0':
         interface = netifaces.ifaddresses('eth0')
         info = interface[netifaces.AF_LINK]
         if info:
            macEth = interface[netifaces.AF_LINK][0]["addr"]
    return macEth

def start():

   macEth        = mac_address()
   currentUnitId = current_unitid()

   # hostipF = "/opt/settings/sys/ip.txt"
   # file = open(hostipF, 'r')
   # host = file.read().strip()
   # file.close()

   #print(host)

   #print(currentUnitId)  


   # Checking the current UnitId for the MacAddr if these are differnt
   if(currentUnitId!=macEth):
      print("Changing UnitId")
      config = ConfigObj(cfg_fn)
      config['general']['unitid'] = macEth
      config.write()

      # if len(currentUnitId) !=0:
      #    subprocess.call("/opt/helena/componets/restartProcess.sh", shell=True)   

   # add the license check here
   config = Config()
   # update config.sys if there is an update from homedots
   license.status(config)

   # add NTP local server configuration
   # ntpstatus = str(subprocess.check_output(["ntpq", "-p"]))
   # print(ntpstatus)
   # if (ntpstatus.find('*') == -1):
   fin = open("/etc/ntp.conf", "rt")
   rip    = config.get('remotedb', 'rip')
   #read file contents to string
   data = fin.read()
   fin.close()
   if (data.find(rip) == -1):
      print(f"NTP is not synchornized a server, thus we add {rip} as a local NTP server to /etc/ntp.conf!")
      #read input file
      fin = open("/opt/helena/conf/ntp.conf", "rt")
      #read file contents to string
      data = fin.read()
      #replace all occurrences of the required string
      data = data.replace('sensorweb.local', rip)
      #close the input file
      fin.close()
      #open the input file in write mode
      fin = open("/opt/helena/conf/ntp.tmp", "wt")
      #overrite the input file with the resulting data
      fin.write(data)
      #close the file
      fin.close()
      subprocess.call("sudo cp /opt/helena/conf/ntp.tmp /etc/ntp.conf && sudo systemctl restart ntpd", shell=True)
   else:
      print(f"NTP is already configured by including {rip} as a local NTP local server in /etc/ntp.conf!")
      # ntpstatus = str(subprocess.check_output(["ntpq", "-p"]))
      # print(ntpstatus)

   #Getting parameters from Cloud
   url = 'https://www.homedots.us/beddot/public/getClient/'+macEth
   #print(url)
   try:
      res = requests.get(url)
      packSize =  len(res.text)
   except Exception:
       packSize = 0

   #Validating for know if we get data
   if(packSize>5):
      array = json.dumps(res.json())
      info = json.loads(array)

      ssid           = info["ssid"]
      unitName       = info["unitName"]
      mac            = info["mac"]
      phoneClient    = info["phoneClient"]
      idUnit         = info["idUnit"]
      idClient       = info["idClient"]
      password       = info["password"]
      alarmStatus    = info["alarmStatus"]
      alarmType      = info["alarmType"]
      envelopeMpd    = info["envelopeMpd"]
      thresholdOnBed = info["thresholdOnBed"]
      extra1         = info["extra1"]
      extra2         = info["extra2"]

   
      # print (ssid)
      # print (unitName)
      # print (mac)
      # print (phoneClient)
      # print (idUnit)
      # print (idClient)
      # print (password)
      # print (alarmStatus)
      # print (alarmType)
      # print (envelopeMpd)
      # print (thresholdOnBed)
      # print (extra1)
      # print (extra2)

     #For alarms parameters
      alarmParameters(alarmStatus,alarmType,envelopeMpd,thresholdOnBed)

      # #Checking current SSID connection name
      # try:
      #     ssidLocal = subprocess.check_output("iwgetid -r", shell = True)
      # except Exception as e:
      #     print(e)

      # if(ssidLocal[len(ssidLocal)-1]==10):
      #    ssidLocal = ssidLocal[0:len(ssidLocal)-1]

      # print (ssidLocal)
      
      # #Switching WiFi connection
      # if(ssid==ssidLocal.decode('utf-8')):
      #    print ("Same WiFi SSID!!!")
      # elif len(ssid) != 0:
      #    print ("Different WiFi SSID!!!")
      #    #subprocess.call("cp /etc/wpa_supplicant/wpa_supplicant.conf wpa_supplicant.conf", shell=True) 
      #    fn = "wpa_supplicant.conf"
      #    f = open(fn, 'w')
      #    f.write('network={\n    ssid="'+ssid+'"\n    scan_ssid=1\n    priority=2\n    psk="'+password+'"\n} \n\n')
      #    f.write('network={\n    ssid="homedots"\n    scan_ssid=1\n    psk="beddot12"\n} \n\n')
      #    #f.write('network={\n    ssid="JosePhone"\n    scan_ssid=1\n    priority=1\n     psk="Pochembe130"\n} \n\n')
      
      #    f.close()

      #    subprocess.call("sudo mv wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf", shell=True)  
      #    time.sleep(5) 
      #    #subprocess.call("sudo reboot", shell=True)

   else:
      print("No DATA from the web endpoint")


if __name__ == '__main__':
   start()

