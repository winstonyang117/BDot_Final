import socket as s
from decimal import Decimal
import subprocess
import configparser


# Parameter from configuation File
config = configparser.ConfigParser()
config.read_file(open(r'../conf/config.sys'))

ip    = config.get('localdb', 'lip')
user  = config.get('localdb', 'luser')
passw = config.get('localdb', 'lpass')

print(ip)
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
http_post  = "curl -s POST \'http://"+ ip+":8086/write?db="+db+"\' -u "+ user+":"+ passw+" --data-binary \' " + "\n address,location="+unit+" ip1="+str(a)
http_post += "\n address,location="+unit+" ip2="+str(b)
http_post += "\n address,location="+unit+" ip3="+str(c)
http_post += "\n address,location="+unit+" ip4="+str(d)
http_post += "\'  &"
print(http_post)
subprocess.call(http_post, shell=True)

http_post  = "curl -s --insecure POST \'https://"+ rip+":8086/write?db="+db+"\' -u "+ ruser+":"+ rpassw+" --data-binary \' " + "\n address,location="+unit+" ip1="+str(a)
http_post += "\n address,location="+unit+" ip2="+str(b)
http_post += "\n address,location="+unit+" ip3="+str(c)
http_post += "\n address,location="+unit+" ip4="+str(d)
http_post += "\'  &"
#print http_post
subprocess.call(http_post, shell=True)




while 1:								# loop forever
    data, addr = sock.recvfrom(1024)	# wait to receive data
#    print data
    data = data.replace(b'}', b'')
    data2 = data.split(b',')							
    timestampi =  Decimal(data2[1].decode())
    timeIni = timestampi * 1000
    count = 0;
    http_post  = "curl -s -POST \'http://"+ ip+":8086/write?db="+db+"\' -u "+ user+":"+ passw+" --data-binary \' "
    http_post2 = "curl -s --insecure -POST \'https://"+rip+":8086/write?db="+db+"\' -u "+ruser+":"+rpassw+" --data-binary \' "

    for f in data2:
       count  = count + 1
       if(count>2):    
#          print int(f)
#          print timeIni
          http_post  += "\nZ,location="+unit+" value=" 
          http_post  += str(int(f)) + " " + str(int(timeIni*1000000))
          if(saveRemoteRaw=='true'):
             http_post2 += "\nZ,location="+unit+" value="
             http_post2 += str(int(f)) + " " + str(int(timeIni*1000000))

          timeIni = timeIni + 10
    
    http_post += "\'  &"
    http_post2 += "\'  &"
    
 #   print http_post
    subprocess.call(http_post, shell=True)
    if(saveRemoteRaw=='true'):
       subprocess.call(http_post2, shell=True)

