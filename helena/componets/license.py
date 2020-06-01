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
    try:
        if config.get('remotedb', 'ruser') != info['username'] or config.get('remotedb', 'rpass') != info['password']:
            config.set('remotedb', 'ruser', info['username'])
            config.set('remotedb', 'rpass', info['password'])
            config.updatedb()
            
    except Exception:
        print("updateconfig exception")
        print(e)

    return 1

def status(config):
    statusK = 0
    packSize = -1
    # word = crypto.config_key
    macEth        = mac_address()
    url = 'https://homedots.us/beddot/public/checkStatus2'
    data = {"mac":"b8:27:eb:dc:80:5c", "version" : "2.0"}

    try:
       res = requests.post(url, data)
       packSize =  len(res.text)
    except Exception:
       packSize = 0

    #Validating for know if we get data
    if(res.status_code ==200):
      try:
        info = res.json()['result']
        status  = int(info["status"])
#        print (status)
#        print (key)
        # uncomment to update
        if status ==0:  # invalid token
            statusK = 0
        elif status ==1: # normal case, good same token 
            # update token            
            statusK = updateconfig(config, info, False)
        elif status ==2: # case, token changed 
            statusK = updateconfig(config, info, True)
        else:           # unknown case
            statusK = 0

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
   time.sleep(3);
   while status(config) ==0:
      time.sleep(10);
      if timeout>0:
         sec += 10
         if sec >timeout:
            return -1
   return 0
 
#status()

