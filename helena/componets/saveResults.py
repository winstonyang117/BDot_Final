import subprocess
import sys, os
import logging
from datetime import datetime

sys.path.insert(0, os.path.abspath('..'))
from componets.config import Config

# Parameters from sys

arg = sys.argv 

serie = arg[1]
field = arg[2]
value = arg[3]
time  = arg[4]

time = time[0:19]
print(time)
print(len(time))
utc_time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S")
epoch_time = int((utc_time - datetime(1970, 1, 1)).total_seconds())

print(serie, field, value, time)

# Parameter from configuation File
# this could be optimized 
config = Config()

ip    = config.get('localdb', 'lip')
user  = config.get('localdb', 'luser')
passw = config.get('localdb', 'lpass')

rip    = config.get('remotedb', 'rip')
ruser  = config.get('remotedb', 'ruser')
rpassw = config.get('remotedb', 'rpass')

db    = config.get('general', 'dbresults')
unit  = config.get('general', 'unitid')

saveRemoteResult = config.get('general', 'saveRemoteResult')

http_post  = "curl -s -POST \'http://"+ ip+":8086/write?db="+db+"\' -u "+ user+":"+ passw+" --data-binary \' "
http_post += "\n"+serie+",location="+unit+" "+field+"="+value+" "+str(epoch_time)+"000000000"  
http_post += "\'  &"

if(saveRemoteResult=='true'):
   http_post2 = "curl -s -POST --insecure \'https://"+rip+":8086/write?db="+db+"\' -u "+ruser+":"+rpassw+" --data-binary \' "
   http_post2 += "\n"+serie+",location="+unit+" "+field+"="+value+" "+str(epoch_time)+"000000000"
   http_post2 += "\'  &"


#print http_post
log = "save.log"
logging.basicConfig(filename=log,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
logging.info(http_post)
    
subprocess.call(http_post, shell=True)

if(saveRemoteResult=='true'):
   subprocess.call(http_post2, shell=True)

