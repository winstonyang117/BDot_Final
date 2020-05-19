import json
import requests
import netifaces
import subprocess
import time
import configparser
import ast
from configobj import ConfigObj



#config = ConfigParser.ConfigParser()
#config.read_file(open(r'./../conf/config.sys'))

#unit  = config.get('general', 'unitid')

#config = ConfigObj('./conf/config.sys')
#config['general']['unitid'] = 'helena10'
#config.write()

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
   config.read_file(open(r'./../conf/config.sys'))

   enablesmson           = parseBoolStringToInt(config.get('messages', 'enablesmson'))
   enablesmsoff          = parseBoolStringToInt(config.get('messages', 'enablesmsoff'))
   enablesmsmovement     = parseBoolStringToInt(config.get('messages', 'enablesmsmovement'))
   envelopeMpdFile       = float(config.get('main', 'mpdEnv')) 
   thresholdOnBedFlie    = float(config.get('main', 'thccMean'))


   config = ConfigObj('./../conf/config.sys')
   
   if(envelopeMpd !=None  and float(envelopeMpd)!=envelopeMpdFile):
      sw = 1
      config['main']['mpdEnv'] = envelopeMpd
      print("Change MDP Envelope")

   if(thresholdOnBed != None and float(thresholdOnBed)!= thresholdOnBedFlie):
      sw = 1
      config['main']['thccMean'] = thresholdOnBed
      print("On/Off th")

   pos = 0
   for alarmt in alarmType: 
     #onBed
     if(alarmt=='1'):
       if(enablesmson!=int(alarmStatus[pos])):
          sw = 1
          print(parseIntToBool(int(alarmStatus[pos])))
          config['messages']['enablesmson'] = parseIntToBool(int(alarmStatus[pos])) 
#          print str(enablesmson)+"  ---  "+alarmStatus[pos]
          print("Change OnBed")

     #offBed
     if(alarmt=='2'):
       if(enablesmsoff!=int(alarmStatus[pos])):
          sw = 1
          config['messages']['enablesmsoff'] = parseIntToBool(int(alarmStatus[pos]))
#          print str(enablesmsoff)+"  ---  "+alarmStatus[pos]
          print("Change OffBed")

     #Movement
     if(alarmt=='3'):
       if(enablesmsmovement!=int(alarmStatus[pos])):
          sw = 1
          config['messages']['enablesmsmovement'] = parseIntToBool(int(alarmStatus[pos]))
#          print str(enablesmsmovement)+"  ---  "+alarmStatus[pos]
          print("Change Movement")

     pos = pos + 1


   if(sw==1):
#     config = ConfigObj('./conf/config.sys')
     config.write()
   
   unit  = config.get('general', 'unitid')
   return unit



def current_unitid():
   config = configparser.ConfigParser()
   config.read_file(open(r'./../conf/config.sys'))

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

macEth        = mac_address()
currentUnitId = current_unitid()

hostipF = "/opt/settings/sys/ip.txt"
file = open(hostipF, 'r')
host = file.read().strip()
file.close()

print(host)

print(currentUnitId)  


# Checking the current UnitId for the MacAddr if these are differnt
if(currentUnitId!=macEth):
   print("Changing UnitId")
   config = ConfigObj('./../conf/config.sys')
   config['general']['unitid'] = macEth
   config.write()
   subprocess.call("/opt/helena/componets/restartProcess.sh", shell=True)   

#Getting parameters from Cloud
url = 'https://www.homedots.us/beddot/public/getClient/'+macEth+'/'+host
print(url)
res = requests.get(url)

packSize =  len(res.text)

#Validating for know if we get data
if(packSize>5):
   array = json.dumps(res.json())
   info = json.loads(array)

   unitName       = info["unitName"]
   mac            = info["mac"]
   phoneClient    = info["phoneClient"]
   idUnit         = info["idUnit"]
   idClient       = info["idClient"]
   alarmStatus    = info["alarmStatus"]
   alarmType      = info["alarmType"]
   envelopeMpd    = info["envelopeMpd"]
   thresholdOnBed = info["thresholdOnBed"]
   extra1         = info["extra1"]
   extra2         = info["extra2"]

   print(unitName)
   print(mac)
   print(phoneClient)
   print(idUnit)
   print(idClient)
   print(alarmStatus)
   print(alarmType)
   print(envelopeMpd)
   print(thresholdOnBed)
   print(extra1)
   print(extra2)

   #For alarms parameters
   alarmParameters(alarmStatus,alarmType,envelopeMpd,thresholdOnBed)    

else:
   print("No DATA")


