import subprocess
import requests
import hashlib
import netifaces
import json
import sys,os
import time

sys.path.insert(0, os.path.abspath('..'))
import componets.crypto as crypto
from componets.config import Config

def updateconfig(config, info, force = False):
    if config.get('remotedb', 'rpass') != info['keyp']:
        config.set('remotedb', 'rpass', info['keyp'])
        config.updatedb()

    return 1

def status(config):
    statusK = 0
    packSize = -1
    # word = crypto.config_key
    word = "abc"
    serial = subprocess.check_output('cat /proc/cpuinfo | grep Serial | awk \'{print($3)}\'', shell=True)[:-1]
    macEth        = mac_address()
    url = 'https://www.homedots.us/beddot/public/checkStatus/'+macEth+'/'+str(serial, 'utf-8')+'/'+word
#    print (url)

    try:
       res = requests.get(url)
       packSize =  len(res.text)
    except Exception:
       packSize = 0

    #Validating for know if we get data
    if(packSize>5):
      try:
        array = json.dumps(res.json())
        info = json.loads(array)
        status  = info["status"]
        key     = info["keyp"]
#        print (status)
#        print (key)
        # uncomment to update
        if status ==0:  # invalid token
            statusK = 0
        elif status ==1: # normal case, good same token 
            # update token            
            # statusK = updateconfig(config, info, False)
            statusK = 1
        elif status ==2: # case, token changed 
            # statusK = updateconfig(config, info, True)
            statusK = 1
        else:           # unknown case
            statusK = 0

        ## todo, rm below code
        m = hashlib.md5()
        m.update(b"abc")
        out = m.hexdigest()
        x = hashlib.md5()
        x.update(out.encode('utf-8'))
        wordp = x.hexdigest()
#        print wordp
#        print key
        if(wordp == key and int(status) == 1):
          statusK = 1
#          print "The Same!!!"
      except Exception:
        statusK = 0
    else:
        statusK = 0

    return int(statusK)

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

def wait_for_license(config, tomeout=0):
   sec = 0
   while status(config) ==0:
      time.sleep(10);
      if timeout>0:
         sec += 10
         if sec >timeout:
            return -1
   return 0
 
#status()

