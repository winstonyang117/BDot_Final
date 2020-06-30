import subprocess
import sys, os
import logging
from datetime import datetime

sys.path.insert(0, os.path.abspath('..'))
from componets.config import Config
import componets.license as license

def saveResults(serie, field, value, time, config):
   time = time[0:19]
 #  print(time)
 #  print(len(time))
   utc_time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S")
   epoch_time = int((utc_time - datetime(1970, 1, 1)).total_seconds())

 #  print(serie, field, value, time)

   db    = config.get('general', 'dbresults')
   unit = license.mac_address()

   saveLocalResult = config.get('general', 'saveLocalResult')
   if(saveLocalResult=='true'):
      ip    = config.get('localdb', 'lip')
      user  = config.get('localdb', 'luser')
      passw = config.get('localdb', 'lpass')

      http_post  = "curl -s -POST \'http://"+ ip+":8086/write?db="+db+"\' -u "+ user+":"+ passw+" --data-binary \' "
      http_post += "\n"+serie+",location="+unit+" "+field+"="+value+" "+str(epoch_time)+"000000000"  
      http_post += "\'  &"

      subprocess.call(http_post, shell=True)

   saveRemoteResult = config.get('general', 'saveRemoteResult')
   if(saveRemoteResult=='true'):
      rip    = config.get('remotedb', 'rip')
      ruser  = config.get('remotedb', 'ruser')
      rpassw = config.get('remotedb', 'rpass')

      http_post2 = "curl -s -POST --insecure \'https://"+rip+":8086/write?db="+db+"\' -u "+ruser+":"+rpassw+" --data-binary \' "
      http_post2 += "\n"+serie+",location="+unit+" "+field+"="+value+" "+str(epoch_time)+"000000000"
      http_post2 += "\'  &"

      subprocess.call(http_post2, shell=True)

if __name__ == '__main__':
   arg = sys.argv
   serie = arg[1]
   field = arg[2]
   value = arg[3]
   time  = arg[4]
   
   saveResults(serie, field, value, time, Config())
