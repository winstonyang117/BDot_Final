import socket as s
import configparser
import time
import urllib3
import sys, os
sys.path.insert(0, os.path.abspath('..'))
import componets.crypto as crypto
import componets.license as license
from componets.config import Config
import subprocess

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def start():
   ##### Global veriables #########

   config = Config()

   ################################

   license.wait_for_license(config)

   # Parameter from configuation Files

   ip    = config.get('localdb', 'lip')
   user  = config.get('localdb', 'luser')
   passw = config.get('localdb', 'lpass')

   rip    = config.get('remotedb', 'rip')
   ruser  = config.get('remotedb', 'ruser')
   rpassw = config.get('remotedb', 'rpass')

   saveRemoteRaw= config.get('general', 'saveRemoteRaw')
   db    = config.get('general', 'dbraw')
   unit  = config.get('general', 'unitid')

   port = 8888								# Port to bind to
   hostipF = "/opt/settings/sys/ip.txt"
   file = open(hostipF, 'r')
   host = file.read().strip()
   file.close()

   print(saveRemoteRaw)
   HP = host + ":" + str(port)
   print("  Opening socket on (HOST:PORT)", HP)

   sock = s.socket(s.AF_INET, s.SOCK_DGRAM | s.SO_REUSEADDR)
   sock.bind((host, port))

   print("Waiting for data on (HOST:PORT) ", HP)

   a,b,c,d = host.split(".")
   addr_data  = "\'address,location={0} ip1={1},ip2={2},ip3={3},ip4={4}\'" \
                     .format(unit, str(a), str(b), str(c), str(d))

   http_post  = "curl -s POST \'http://"+ ip+":8086/write?db="+db+"\' -u "+ user+":"+ passw+" --data-binary " + addr_data
   print(http_post)
   subprocess.call(http_post, shell=True)

   http_post  = "curl -s --insecure POST \'https://"+ rip+":8086/write?db="+db+"\' -u "+ ruser+":"+ rpassw+" --data-binary " + addr_data
   print(http_post)
   subprocess.call(http_post, shell=True)

   pkt_rate = 4  # 4 pkt per second
   num_pkt = 0

   while 1:		# loop forever
      data = sock.recv(1024)	# wait to receive data

      num_pkt += 1
   #   multiple dataset with same timestamp 
   #   t0 = time.monotonic()
      data = data.rstrip(b'}').split(b',')
      data.pop(0)
      timeIni = int(float(data.pop(0))*1000) * 1000000
      http_post  = "curl -s -POST \'http://"+ ip+":8086/write?db="+db+"\' -u "+ user+":"+ passw+" --data-binary \' "
      http_post2 = "curl -s --insecure -POST \'https://"+rip+":8086/write?db="+db+"\' -u "+ruser+":"+rpassw+" --data-binary \' "

      for f in data:
         http_post  += "\nZ,location={0} value={1} {2}".format(unit,int(f), timeIni)

         if(saveRemoteRaw=='true'):
             http_post2 += "\nZ,location={0} value={1} {2}".format(unit,int(f), timeIni)
         
         timeIni = timeIni + 10000000

      http_post += "\'  &"
      http_post2 += "\'  &"

      subprocess.call(http_post, shell=True)
      if(saveRemoteRaw=='true'):
          subprocess.call(http_post2, shell=True)

   #   t1 = time.monotonic()
   #   print("t1-t0= " +str(t1-t0))

   #  every 5 minutes
      if num_pkt %(pkt_rate*60*5) ==0:
         license.wait_for_license(config)


if __name__ == '__main__':
   start()
