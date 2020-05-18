import socket as s
from decimal import Decimal
import configparser
import time
from influxdb import InfluxDBClient
import urllib3
import sys, os
sys.path.insert(0, os.path.abspath('..'))
import componets.crypto as crypto
import componets.license as license
from componets.config import Config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

##### Global veriables #########

config = Config()

################################

while license.status(config) ==0:
   time.sleep(10);

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

local_db_conn = InfluxDBClient(host=ip, port="8086", username=user, password=passw, database=db)
remote_db_conn = InfluxDBClient(host=rip, port="8086", username=ruser, password=rpassw, database=db,ssl=True,verify_ssl=False)

a,b,c,d = host.split(".")
addr_data  = "address,location={0} ip1={1},ip2={2},ip3={3},ip4={4}" \
                  .format(unit, str(a), str(b), str(c), str(d))

print(addr_data)
local_db_conn.write_points(addr_data, protocol='line')
remote_db_conn.write_points(addr_data, protocol='line')


while 1:								# loop forever
    data, addr = sock.recvfrom(1024)	# wait to receive data
#   multiple dataset with same timestamp 
    data = data.replace(b'}', b'')
    data2 = data.split(b',')							
    timestampi =  Decimal(data2[1].decode())
    timeIni = timestampi * 1000

    count = 0;
    data_set = []
    for f in data2:
       count  = count + 1
       if(count>2):    
#          print int(f)
#          print timeIni
          data_set.append("Z,location={0} value={1} {2}" \
                           .format(unit, str(int(f)), str(int(timeIni*1000000))))
          
          timeIni = timeIni + 10
    
    local_db_conn.write_points(data_set, protocol='line')
    if(saveRemoteRaw=='true'):
       remote_db_conn.write_points(data_set, protocol='line')


