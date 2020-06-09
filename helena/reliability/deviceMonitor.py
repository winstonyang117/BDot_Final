#!/usr/bin/env python3
import psutil
import subprocess
import time
import os, sys

sys.path.insert(0, os.path.abspath('..'))
from componets.config import Config
import componets.license as license

def measure_temp():
        temp = os.popen("vcgencmd measure_temp").readline()
        temp = temp[:-3]
        return (temp.replace("temp=",""))

#temperature = measure_temp()

def start():

   config = Config()

   ip    = config.get('localdb', 'lip')
   user  = config.get('localdb', 'luser')
   passw = config.get('localdb', 'lpass')
   db    = config.get('general', 'dbstatus')
   memoryth  = config.get('system', 'memory')
   cputh     = config.get('system', 'cpu')

   rip    = config.get('remotedb', 'rip')
   ruser  = config.get('remotedb', 'ruser')
   rpassw = config.get('remotedb', 'rpass')

   saveRemoteRaw= config.get('general', 'saveRemoteRaw')

   unit = license.mac_address()
   cpu = psutil.cpu_percent(interval=1)
   mem = psutil.virtual_memory().percent
   diskp= psutil.disk_usage('/').percent
   diskt= (psutil.disk_usage('/').used)/1027/1024
   temperature = measure_temp()

   http_postm = ""
   http_post = "curl -s -POST \'http://"+ip+":8086/write?db="+db+"\' -u "+user+":"+passw+" --data-binary \'"
   http_postm = http_postm + " \n memory,location="+unit+" value=" +str(mem)
   http_postm = http_postm + " \n cpu,location="+unit+" value="+ str(cpu)
   http_postm = http_postm + " \n diskusagepercent,location="+unit+" value=" + str(diskp)
   http_postm = http_postm + " \n temperature,location="+unit+" value=" + temperature
   http_postm = http_postm + " \n diskusedsize,location="+unit+" value="+ str(diskt) + " \'  "
   http_post = http_post + http_postm
   subprocess.call(http_post, shell=True)

   if(saveRemoteRaw=='true'):
      http_post2 = "curl -s --insecure -POST \'https://"+rip+":8086/write?db="+db+"\' -u "+ruser+":"+rpassw+" --data-binary \'"
      http_post2 = http_post2 + http_postm
      subprocess.call(http_post2, shell=True)


   sw    = 1
   tries = 0
   while sw:
      sw = 0
      tries = tries + 1
      if int(mem) > int(memoryth):
         sw = 1
         mem = psutil.virtual_memory().percent
         print("system for memory")

      if int(cpu) > int(cputh):
         sw = 1
         cpu = psutil.cpu_percent(interval=1)
         print("system for cpu")
      
      if(tries == 2):
         print("RESTARTING")
         os.system("sudo systemctl reboot");
   
      time.sleep (5)
      

if __name__ == '__main__':
   start()


