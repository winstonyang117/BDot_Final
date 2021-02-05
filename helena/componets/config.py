import configparser
import sys, os
import shutil
sys.path.insert(0, os.path.abspath('..'))
import componets.crypto as crypto

license_key = b'W__MSG7tzKO9Tah5-WoExXhylLEUK7UBkAPEvzZBno0='

if getattr(sys, 'frozen', False):
   dir = r'/opt/helena'
else:
   dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'../') 

cfg_fn =  os.path.join(dir, 'conf/config.sys')
# sec_cfg_fn = os.path.join(dir, 'conf/config.sec')

class Config:
 
  def __init__(self):
    self._config = configparser.ConfigParser()
    self._config.read_file(open(cfg_fn))

    # self._dbconfig = configparser.ConfigParser()
    # cfgdata = crypto.decrypt_file(sec_cfg_fn , license_key)
    # self._dbconfig.read_string(cfgdata.decode())

  def get(self, section, key):
    # if section == "localdb" or section == "remotedb":
    #   return self._dbconfig.get(section, key)
    # else:
      return self._config.get(section, key)

  def set(self, section, key, val):
    # if section == "localdb" or section == "remotedb":
    #   return self._dbconfig.set(section, key, val)
    # else:
      return self._config.set(section, key, val)

  def updatedb(self):
    # old = sec_cfg_fn + '.old'
    # shutil.copy(sec_cfg_fn, old)

    # cfg_new = sec_cfg_fn #+ '.new'
    # with open(cfg_new, 'w') as configfile:
    #   self._dbconfig.write(configfile)

    # crypto.encrypt_file(cfg_new, license_key, sec_cfg_fn)

    # old = cfg_fn + '.old'
    # shutil.copy(cfg_fn, old)

    cfg_new = cfg_fn #+ '.new'
    with open(cfg_new, 'w') as configfile:
      self._config.write(configfile)


