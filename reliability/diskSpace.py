#!/usr/bin/env python
import psutil
import subprocess
import configparser
import time
import datetime
import os
from influxdb import InfluxDBClient

config = configparser.ConfigParser()
config.read_file(open(r'../conf/config.sys'))
ip    = config.get('localdb', 'lip')

user  = config.get('localdb', 'luser')
passw = config.get('localdb', 'lpass')

db         = config.get('general', 'dbraw')
unit       = config.get('general', 'unitid')

daysRemove = config.get('system', 'daystoremove')
diskth     = config.get('system', 'disk')

daysRemove =  float(daysRemove)*86400
epochWeek =  float(7)*86400


diskp= psutil.disk_usage('/').percent
diskt= (psutil.disk_usage('/').used)/1027/1024

if(float(diskp) > float(diskth)):
  print("remove last day")
  query = 'SELECT "value" FROM Z WHERE ("location" = \''+unit+'\')  ORDER BY time ASC LIMIT 1'
  
  client = InfluxDBClient(ip, "8086", user, passw, db)

  result = client.query(query)
  points = list(result.get_points())

  for point in points:
     stampIni = point['time']
     break;
  
  epoch = time.mktime(datetime.datetime.strptime(stampIni, "%Y-%m-%dT%H:%M:%S.%fZ").timetuple())
  epoch = epoch + daysRemove
  millisIni =  datetime.datetime.strptime(stampIni, "%Y-%m-%dT%H:%M:%S.%fZ")
  stampEnd = (datetime.datetime.utcfromtimestamp(epoch).strftime('%Y-%m-%dT%H:%M:%S.'))
  stampEnd = stampEnd + str(millisIni.microsecond) + 'Z'

  query = "delete from Z where location='"+unit+"' and time>='"+stampIni+"' and time<='"+stampEnd+"'";
  print(query)
  client.query(query)

currentEpochTime = int(time.time())
lastWeekEpochTime = currentEpochTime - epochWeek 
startingTime =  (datetime.datetime.utcfromtimestamp(lastWeekEpochTime).strftime('%Y-%m-%dT%H:%M:%S'))
print(startingTime)

query = "delete from Z where time<'"+startingTime+"Z'";
#print query
client = InfluxDBClient(ip, "8086", user, passw, db)
client.query(query)
