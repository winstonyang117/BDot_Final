from scipy.signal import butter, lfilter
from scipy import signal
from datetime import datetime, date
from influxdb import InfluxDBClient
import numpy
import random
import time
import operator
import sys, os
import logging
import algorithm as dsp
#from scipy import stats
import nitime.algorithms as nt_alg
import numpy as np
from numpy import array
import scipy as sp
import threading
from datetime import datetime
from dateutil import tz
import pytz
import ast
import requests

sys.path.insert(0, os.path.abspath('..'))
import componets.license as license
import componets.saveResults as SaveToDB
from componets.config import Config

# from dl_alg import DL_Model

######################################### Functions #################################################################

def parseBoolString(theString):
  return theString[0].upper()=='T'

# Sending Alerts
def send_alert(url, alert_type, user=None, pwd=None):
   http = url + "/" + license.mac_address() + "/" +str(alert_type)

   try:
      requests.get(http)
   except Exception as e:
      print(e)
   

##### removed algorithms from here  ####

def utcToLocalTime(time2, formatt, from_zone, to_zone):
    utc = datetime.strptime(time2, formatt)
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    timeDetected = central.strftime("%m-%d %I:%M %p")
    return timeDetected

def saveResults(serie, field, value, time, config):
    SaveToDB.saveResults(serie, field, value, time, config)
    
########### main entrance ########
def main():
 config = Config()

 # Song 1/26/2021 diable check forever to allow local deployment
#  statusKey = license.wait_for_license(config) is 0
 license.status(config)
 statusKey = True

 
 formatt = '%Y-%m-%dT%H:%M:%S.%fZ'
 from_zone = tz.tzutc()
 to_zone = pytz.timezone("America/New_York")

 # Parameters from Config file
 
 ip    = config.get('localdb', 'lip')
 user  = config.get('localdb', 'luser')
 passw = config.get('localdb', 'lpass')

 debug = config.get('general', 'debug')
 debug = parseBoolString(debug)
 
 db           = config.get('general', 'dbraw')
 buffersize   = config.get('general', 'buffersize')
 samplingrate = int(config.get('general', 'samplingrate'))

 # Parameters for Component 1 --> OnBed
 onBedTimeWindow   = int(config.get('main', 'onBedTimeWindow'))
 lowCut            = float(config.get('main', 'lowCut'))
 highCut           = float(config.get('main', 'highCut'))
 order             = int(config.get('main', 'order'))
 onBedThreshold    = int(config.get('main', 'onBedThreshold'))
 timeCheckingOnBed = int(config.get('main', 'timeCheckingOnBed'))
 thratio           = float(config.get('main', 'ratioThreshold'))
 thsd              = float(config.get('main', 'sdThreshold'))
 thon              = int(config.get('main', 'secondsForOn'))
 thoff             = int(config.get('main', 'secondForOff'))
 thccMean          = float(config.get('main', 'thccMean'))
 mpdEnv            = int(config.get('main', 'mpdEnv'))

 # Added by Song on check max energy in the past energyWindow seconds
 # check large energy events
#  indexEnergy = 0
#  maxEnergy = 0
#  energyWindow = int(config.get('main', 'energyWindow')) # 12 # a large events with energyWindow seconds
#  energyThreshold = int(config.get('main', 'energyThreshold')) #100000
#  energyList = np.zeros(energyWindow)
 # end add 10/20/2020

 # Parameters for Component 2 --> Movement
 movementTimeWindow   = int(config.get('main', 'movementTimeWindow'))
 movementThreshold    = int(config.get('main', 'movementThreshold'))
 timeCheckingMovement = int(config.get('main', 'timeCheckingMovement'))


 # Parameters for Component 3 --> HeartbeatRate
 hrTimeWindow    = int(config.get('main', 'hrTimeWindow'))
 timeCheckingHR  = int(config.get('main', 'timeCheckingHR'))

 # Parameters for Component 4 --> Posture Change
 postureChangeTimeWindow = int(config.get('main', 'postureChangeTimeWindow'))

 # Messages
 alert_url    = config.get('messages', 'alert_url')
 enablesmson       = True #parseBoolString(config.get('messages', 'enablesmson'))
 enablesmsoff      = True #parseBoolString(config.get('messages', 'enablesmsoff'))
 enablesmsmovement = True #parseBoolString(config.get('messages', 'enablesmsmovement'))
 unit = license.mac_address()

# print messmovement
 # Constant Calculations
 maxbuffersize               = int(buffersize) * int(samplingrate)

 elementsNumberOnBed         = onBedTimeWindow * samplingrate

 elementsNumberMovement      = movementTimeWindow * samplingrate

 elementsNumberHR            = hrTimeWindow * samplingrate

 elementsNumberPostureChange =  postureChangeTimeWindow * samplingrate

 # DB Conection
 try: 
   client = InfluxDBClient(ip, "8086", user, passw, db)
 except Exception as e:
   print("main(), DB access error:")
   print(e)
   # syslog.syslog('Rebooting due to helena unable to connect to influxDB')
   # remove license for now by Song 10/22/2020
   #license.wait_for_license(config)

 # Buffers for time and
 buffer      = []
 buffertime  = []

 previousHBSignal = []
 currentHBSignal  = []

 onBed       = False
 counterTime = 0
 counterNonBed = 0
 counterStable = 0
 previousFloorEventTime = 0

 movement = False

 # Time for showing the movement message
 movementShowDelay = 0

 # Counter for data without movement
 hrSignalNoNoise = 0


 #Values fro HR calcullation
 start = time.process_time()
 N = elementsNumberHR
 nfft = np.power( 2, int(np.ceil(np.log2(N))) )
 NW = 46 #50
 (dpss, eigs) = nt_alg.dpss_windows(N, NW, 2*NW)
 keep = eigs > 0.9
 dpss = dpss[keep]; eigs = eigs[keep]
 fm = int( np.round(float(200) * nfft / N) )
 print(time.process_time() - start)

# Getting the system current time
 current = datetime.utcnow()

# Determining the starting point of the buffer using epoch time
 epoch2 = int( (current - datetime(1970,1,1)).total_seconds())

 # Parameters for the Query
 epoch2 = epoch2 - 1
 epoch1 = epoch2 - 1

 # counterFalseOnBed
 counterFalseOnBed = 0

 counteron  = 0
 counteroff = 0

 prevalues = []
 preMovements = []
 pOnBed = False
 sumMovements = 0

 num_failures = 0

#  alg = DL_Model()
#  alg.load_model('../models/DL_net_model/')

 # Infinite Loop
 while True:
    if(debug): print("*****************************************"+str(statusKey))
    stampIni = (datetime.utcfromtimestamp(epoch1).strftime('%Y-%m-%dT%H:%M:%S.000Z'))
    stampEnd = (datetime.utcfromtimestamp(epoch2).strftime('%Y-%m-%dT%H:%M:%S.000Z'))
    #t0 = time.perf_counter()
    if(debug): print(stampIni)
    if(debug): print(stampEnd)
    query = 'SELECT "value" FROM Z WHERE ("location" = \''+unit+'\')  and time >= \''+stampIni+'\' and time <= \''+stampEnd+'\'   '
    
    try:
       result = client.query(query)
       if result.error ==None:
          num_failures = 0
       else:
          num_failures = num_failures +1
          syslog.syslog('Failure in influxDB query: {0}'.format(result.error))

    except Exception as e:
       num_failures = num_failures +1
       syslog.syslog('Exception in influxDB query: {0}'.format(e))

    if num_failures != 0:       
       if num_failures > 3:
          syslog.syslog('Rebooting due to helena unable to connect to influxDB')
          os.system("sudo systemctl reboot");

       client.close()
       time.sleep(2)

       try:
          client = InfluxDBClient(ip, "8086", user, passw, db)
       except Exception as e:
          print("main(), DB access error in loop:")
          print(e)
         # remove license for now by Song 10/22/2020
         #license.wait_for_license(config)

       continue

    points = list(result.get_points())

    values =  list(map(operator.itemgetter('value'), points))
    times  =  list(map(operator.itemgetter('time'),  points))

    buffertime = buffertime + times
    buffer     = buffer + values
    buffLen    = len(buffer)
    # Cutting the buffer
    if(buffLen > maxbuffersize):
       difSize = buffLen - maxbuffersize
       del buffer[0:difSize]
       del buffertime[0:difSize]

    if(buffLen>0):
       if(debug): print("Buffer Time:    " + str(buffertime[0]) + "  -   " + str(buffertime[len(buffertime)-1]))

    if(debug): print(buffLen)
    #################################################################
    #OnBed
    #################################################################
    buffLen    = len(buffer)


    #t1 = time.perf_counter()
    #print("t1-t0= " +str(t1-t0))

# On/Off correlation
    if(statusKey):
     if(buffLen>=elementsNumberOnBed and counterTime%timeCheckingOnBed == 0 ):
       #t2 = time.perf_counter()

       signalToOnBed = buffer[buffLen-elementsNumberOnBed:buffLen]

       peaksCR = dsp.checkOnBedCR(signalToOnBed,buffertime[len(buffertime)-1])
       nowtime = buffertime[len(buffertime)-1]

       # Added by Song on check max energy in the past energyWindow seconds
      #  energyList[indexEnergy] = np.std(np.asarray(signalToOnBed))
      #  indexEnergy = (indexEnergy + 1)%energyWindow
      #  maxEnergy = max(energyList)
       # end add on 10/20/2020
       
       #t3 = time.perf_counter()
       #print("t3-t2= " +str(t3-t2))
       saveResults('corrStatus', 'bs10' ,str(peaksCR), nowtime, config)
       if(peaksCR > thccMean):
           prevalues.append(1)
       else:
           prevalues.append(0)

       if(len(prevalues)>20):
          prevalues = prevalues[1:]
          a = numpy.asanyarray(prevalues)
          ccMean = a.mean()
       else:
          ccMean = 1000

       if ( peaksCR < thccMean and ccMean <= 0.5 ):
          counteron  = counteron + 1
          if(counteron>100):
             counteron = counteron - 50
          counteroff = 0
       elif (ccMean <= 1):
          counteroff = counteroff +1
          if(counteroff > 100):
             counteroff = counteroff - 50
          counteron = 0
       if(debug):
         if(debug): print(" Peaks:", peaksCR, " Mean:", ccMean, " On:", counteron, " Off:", counteroff)
     
      # edited by Song on 10/20/2020 to add check of maxEnergy
       #if(counteron > thon and maxEnergy > energyThreshold):
       if(counteron > thon):
      # end edit by Song on 10/20/2020
          #saveON
          if(enablesmson and onBed == False):
             timeDetected = utcToLocalTime(buffertime[len(buffertime)-thon], formatt, from_zone, to_zone)
             sendEmailT = threading.Thread(target=send_alert, args=(alert_url, 1))
             sendEmailT.start()
          saveResults('bedStatus', 'bs' ,'1', buffertime[len(buffertime)-thon], config)
          onBed = True
          pOnBed = True
      # edited by Song on 10/20/2020 to add check of maxEnergy
      #  elif(counteroff > thoff and maxEnergy > energyThreshold):
       elif(counteroff > thoff):
      # end edit by Song on 10/20/2020
          if(enablesmsoff and onBed == True):
             timeDetected = utcToLocalTime(buffertime[len(buffertime)-thoff], formatt, from_zone, to_zone)
             sendEmailT = threading.Thread(target=send_alert, args=(alert_url, 2))
             sendEmailT.start()
          #saveOFF
          saveResults('bedStatus', 'bs' ,'0', buffertime[len(buffertime)-thoff], config)
          onBed  = False
          pOnBed = False
          hrSignalNoNoise = 0
       else:
          #Calculing
         # removed by Song on 10/16/2020
         #  saveResults('bedStatus', 'bs' ,'2', buffertime[len(buffertime)-1], config)
          if(onBed):
             saveResults('bedStatus', 'bs' ,'1', buffertime[len(buffertime)-1], config)
          else:
             saveResults('bedStatus', 'bs' ,'0', buffertime[len(buffertime)-1], config)
         # end replacement by Song on 10/16/2020
          pOnBed = True

    #################################################################
    #movement
    ################################################################
     if((onBed or pOnBed) and buffLen>=elementsNumberMovement and counterTime%timeCheckingMovement == 0 ):
       movementShowDelay = movementShowDelay + 1
       signalToMovement = buffer[buffLen-elementsNumberMovement:buffLen]
       movement = dsp.checkMovement(signalToMovement, movementThreshold, buffertime[len(buffertime)-1], movementShowDelay)
       nowtime = buffertime[len(buffertime)-1]
       if not (movement):
        # saveResults('posture', 'x' ,'5', nowtime, config)
          hrSignalNoNoise = hrSignalNoNoise + timeCheckingMovement
          preMovements.append(0)
       else:
          saveResults('posture', 'x' ,'7', nowtime, config)

          preMovements.append(1)
          sumMovements = sum(preMovements)
          if(enablesmsmovement and sumMovements > 15):
             timeDetected = utcToLocalTime(buffertime[len(buffertime)-1], formatt, from_zone, to_zone)
             sendEmailT = threading.Thread(target=send_alert, args=(alert_url, 3))
             #sendEmailT = threading.Thread(target=send_email, args=(companyemail,mailpass,recipients,subject,messmovement))
             sendEmailT.start()
             preMovements = []

       if(len(preMovements)>60):
          preMovements = preMovements[1:]

       if (movement or movementShowDelay>100000):
          movementShowDelay = 0
          hrSignalNoNoise   = 0
       if(debug): print('movement:',movement, ' Counter',counterTime)


    #################################################################
    #Hearthbeat Rate
    #################################################################
     if(debug): print('Counter of Not Noise ',hrSignalNoNoise)
     if(onBed and counteroff<25 and buffLen>=elementsNumberHR and counterTime%timeCheckingHR == 0 and hrSignalNoNoise>= hrTimeWindow ):
        if(debug): print("Calculating HBR")
        # If we can calculate the HBR is because someone is OnBed
#        saveResults('bedStatus', 'bs' ,'1', buffertime[len(buffertime)-1])
        signalToHBR = buffer[buffLen-elementsNumberHR:buffLen]
        nowtime = buffertime[len(buffertime)-1]

      #   [bph, bpl] = alg.predict(np.asarray(signalToHBR))
      #   saveResults('vitalsigns', 'systolic', str(bph), nowtime, config)
      #   saveResults('vitalsigns', 'diastolic', str(bpl), nowtime, config)

#        hbr = dsp.calculateHBR(signalToHBR, lowCut, highCut, samplingrate, order, buffertime[len(buffertime)-1])
#        hbr = dsp.calculateHBR2(signalToHBR, fm, eigs, dpss, nfft, buffertime[len(buffertime)-1])
        signalFiltered = dsp.butter_bandpass_filter(signalToHBR, lowCut, highCut, samplingrate, order)
        hbr,rr = dsp.calculateHBR3(signalFiltered, fm, eigs, dpss, nfft, buffertime[len(buffertime)-1],mpdEnv)

        saveResults('hrate', 'hr' ,str(hbr), nowtime, config)
        saveResults('rrate', 'rr' ,str(rr), nowtime, config)
        if(hbr > 30):
#            if(debug): print "HBR greater than 30 --> ",hbr
            previousHBSignal = buffer[buffLen-elementsNumberPostureChange:buffLen]

    #################################################################
    # Posture Change
    #################################################################
     if(counterStable >= 0 and onBed and len(previousHBSignal)>0):
      counterStable = counterStable + 1
     else:
      counterStable = -1
     if(movement):
       counterStable = 0
     if(not onBed):
       counterStable = -1
       previousHBSignal = []
     if(counterStable == postureChangeTimeWindow + 5):
       counterStable = -1
       currentHBSignal = buffer[buffLen-elementsNumberPostureChange:buffLen]
       percent = dsp.calculatePostureChange(previousHBSignal, currentHBSignal, buffertime[len(buffertime)-1])
       nowtime = buffertime[len(buffertime)-1]
       saveResults('change', 'x' ,str(percent), nowtime, config)
     # previousHBSignal
       previousHBSignal = currentHBSignal
    #################################################################


     ################################################################
     # Out bed Events
     elementsNumberFall = 300
     ################################################################

     if(not onBed and buffLen>=elementsNumberFall and counterTime%timeCheckingMovement == 0 and counterTime-previousFloorEventTime > 5):
       counterNonBed = counterNonBed + 1
     else:
       counterNonBed = 0

    # Cheking is the process need to sleep
    current = int( (datetime.utcnow() - datetime(1970,1,1)).total_seconds())
    epoch2 = epoch2 + 1
    epoch1 = epoch1 + 1
#    print epoch2

    counterTime = counterTime + 1


    # Updating parameters every 5 minutes
    if(counterTime%300 == 0):
       if(debug): print("-----------------------------------------------------------------------")
       config = Config()

       enablesmson       = True #parseBoolString(config.get('messages', 'enablesmson'))
       enablesmsoff      = True #parseBoolString(config.get('messages', 'enablesmsoff'))
       enablesmsmovement = True #parseBoolString(config.get('messages', 'enablesmsmovement'))
       thccMean          = float(config.get('main', 'thccMean'))
       mpdEnv            = int(config.get('main', 'mpdEnv'))
       debug = config.get('general', 'debug')
       debug = parseBoolString(debug)

       if(debug): print(thccMean)
       if(debug): print(mpdEnv)
    
      # remove license for now by Song 10/22/2020
      #  statusKey = license.wait_for_license(config) is 0
       license.status(config)

    if(counterTime > 100000):
       counterTime = counterTime - 100000

   # time.sleep(1)
    if ( (current-epoch2) < 1):
        time.sleep(1)
        if(debug): print("*********")

#    log = "otro.log"
#    logging.basicConfig(filename=log,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
#    logging.info('HERE...')

if __name__== '__main__':
  main()
