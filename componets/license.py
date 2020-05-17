import subprocess
import requests
import hashlib
import netifaces
import json
if __name__ == "__main__":
    import crypto
else:
    import componets.crypto
    
def status():
    statusK = 0
    packSize = -1
    sw = 0
    # word = crypto.config_key
    word = "abc"
    serial = subprocess.check_output('cat /proc/cpuinfo | grep Serial | awk \'{print($3)}\'', shell=True)[:-1]
    macEth        = mac_address()
#    url = 'http://beddots.local/checkStatus/'+macEth+'/'+serial+'/'+word
    url = 'https://www.homedots.us/beddot/public/checkStatus/'+macEth+'/'+str(serial, 'utf-8')+'/'+word
#    print url

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
#        print status
#        print key
        
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
        sw = 1

#    print '-----------'
#    print sw
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

#status()
