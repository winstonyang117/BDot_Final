import ConfigParser
from configobj import ConfigObj
from datetime import datetime
from dateutil import tz
import pytz


#formatt = '%Y-%m-%dT%H:%M:%S.%fZ'
#from_zone = tz.tzutc()
#to_zone = pytz.timezone("America/New_York")


def utcToLocalTime(time2, formatt, from_zone, to_zone):
    if(len(time2)<21):
      print "OTRO FORMATO"
      formatt = '%Y-%m-%dT%H:%M:%SZ'
    utc = datetime.strptime(time2, formatt)
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    timeDetected = central.strftime("%m-%d %I:%M %p")
    return timeDetected



formatt = '%Y-%m-%dT%H:%M:%S.%fZ'
from_zone = tz.tzutc()
to_zone = pytz.timezone("America/New_York")

time2 = '2019-07-25T18:07:57Z'; 
print utcToLocalTime(time2, formatt, from_zone, to_zone)


#config = ConfigParser.ConfigParser()
#config.readfp(open(r'./conf/config.sys'))


#unit  = config.get('general', 'unitid')

#config = ConfigObj('./conf/config.sys')
#config['general']['unitid'] = 'helena10'
#config.write()
