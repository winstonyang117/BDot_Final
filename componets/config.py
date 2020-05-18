import configparser
import sys, os

sys.path.insert(0, os.path.abspath('..'))
import componets.crypto as crypto

license_key = b'W__MSG7tzKO9Tah5-WoExXhylLEUK7UBkAPEvzZBno0='

cfg_fn = os.path.dirname(__file__) + r'/../conf/config.sys'
db_cfg_fn = os.path.dirname(__file__) + r'/../conf/config.sec'

class Config:
 
  def __init__(self):
    self._config = configparser.ConfigParser()
    self._config.read_file(open(cfg_fn))

    self._dbconfig = configparser.ConfigParser()
    cfgdata = crypto.decrypt_file(db_cfg_fn , license_key)
    self._dbconfig.read_string(cfgdata.decode())

  def get(self, section, key):
    if section == "localdb" or section == "remotedb":
      return self._dbconfig.get(section, key)
    else:
      return self._config.get(section, key)

