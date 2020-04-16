import json
import requests
import netifaces
import subprocess
import sys
import time
import ConfigParser
import ast
from configobj import ConfigObj


def startHelena():
  check = 'ps aux | grep "helenaservice.sh"'
  result = subprocess.check_output(check, shell=True)
  try:
    x = result.index('/bin/bash')
    print "runnig"
  except Exception:
    result = subprocess.check_output('sudo systemctl start helena', shell=True)
    print "NO"

  print result

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


def status():
 secs = 5
 serial = subprocess.check_output('cat /proc/cpuinfo | grep Serial | awk \'{print($3)}\'', shell=True)[:-1]
 macEth        = mac_address()
# macEth = serial
# url = 'http://beddots.local/unitStatus/'+macEth+'/'+serial+'/abc'
 url = 'http://www.homedots.us/beddot/public/unitStatus/'+macEth+'/'+serial+'/abc'

 print url
 
 while( 6 > 5 ): 
  sw = 0
#  macEth        = mac_address()
#  url = 'http://beddots.local/unitStatus/'+macEth
  
  try:
    res = requests.get(url)
  except Exception:
    sw = 1
    time.sleep(secs)
    continue
   
  packSize =  len(res.text)
  print res
  #Validating for know if we get data
  if(packSize>5):
    try:
      array = json.dumps(res.json())
      info = json.loads(array)
    except Exception:
      sw = 1
      time.sleep(secs)
      continue
 

    status  = int(info["status"])
    key     = info["key"]
    print "------------"
    print status
    print key
    str2 = 'sudo echo "'+str(key)+'" > key2'
    cmp_serial = subprocess.check_output(str2, shell=True)
    subprocess.check_output("sudo cp key2 ../key", shell=True)    
    cmp_serial = subprocess.check_output('sudo openssl enc -a -d -aes-256-cbc -pass pass:sensorweb987 -in key2',shell=True)   
    print cmp_serial

    if status == 1 or status == 2:
       print "DONE"
       if status == 1:
          cmp_serial = subprocess.check_output("sudo cp key2 ../key", shell=True)
          startHelena()
          break
       else:
	  time.sleep(3)
    else:
       print "Waiting"
       time.sleep(3)
       
 
def main():
   status()

if __name__=="__main__":
   main()

 
