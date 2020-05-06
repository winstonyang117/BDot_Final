import urllib3
import netifaces
from scipy.signal import butter, lfilter
from scipy import signal
from datetime import datetime, date
from influxdb import InfluxDBClient
from operator import attrgetter
import numpy
import subprocess
import random
import time
import operator
import configparser
import sys
import logging
from algorithm import *
from scipy.stats import kurtosis
from scipy import stats
import nitime.algorithms as nt_alg
import nitime.utils as nt_ut
import numpy as np
from numpy import array
import scipy as sp
import threading
from datetime import datetime
from dateutil import tz
import pytz
import smtplib
import ast
#import statsmodels.api as sm
import json
import requests



######################################### Functions #################################################################

def parseBoolString(theString):
  return theString[0].upper()=='T'

# Sending Alerts
def send_email(user, pwd, recipient, subject, body):

#    print recipient
    FROM = user
    TO = recipient if isinstance(recipient, list) else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print('successfully sent the mail')
    except:
        print("failed to send mail")

##### removed algorithms from here  ####

def utcToLocalTime(time2, formatt, from_zone, to_zone):
    utc = datetime.strptime(time2, formatt)
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    timeDetected = central.strftime("%m-%d %I:%M %p")
    return timeDetected

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


def status():
    statusK = 0
    packSize = -1
    sw = 0
    word = "abc"
    serial = subprocess.check_output('cat /proc/cpuinfo | grep Serial | awk \'{print($3)}\'', shell=True)[:-1]
    macEth        = mac_address()
#    url = 'http://beddots.local/checkStatus/'+macEth+'/'+serial+'/'+word
    url = 'http://www.homedots.us/beddot/public/checkStatus/'+macEth+'/'+str(serial, 'utf-8')+'/'+word
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
        import hashlib
        m = hashlib.md5()
        m.update("abc")
        out = m.hexdigest()
        x = hashlib.md5()
        x.update(out)
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

#########################################################################################################################

def saveResults(serie, field, value, time):
    p1 = subprocess.Popen(['python', 'componets/saveResults.py', serie, field , value, time],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)

def main():
 statusKey  = status()
 formatt = '%Y-%m-%dT%H:%M:%S.%fZ'
 from_zone = tz.tzutc()
 to_zone = pytz.timezone("America/New_York")
 # Parameters from Config file
 config = configparser.ConfigParser()
 config.read_file(open(r'./conf/config.sys'))

 debug = config.get('general', 'debug')
 debug = parseBoolString(debug)
 ip    = config.get('localdb', 'lip')
 user  = config.get('localdb', 'luser')
 passw = config.get('localdb', 'lpass')

 db           = config.get('general', 'dbraw')
 unit         = config.get('general', 'unitid')
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

 companyemail    = config.get('messages', 'companyemail')
 mailpass        = "S3nsorweb"
 personname      = config.get('messages', 'personname')
 recipients      = ast.literal_eval(config.get('messages', 'recipients'))

 subjecton       = config.get('messages', 'subjecton') + " "
 subjectoff      = config.get('messages', 'subjectoff') + " "
 subjectmovement = config.get('messages', 'subjectmovement') + " "

 enablesmson       = parseBoolString(config.get('messages', 'enablesmson'))
 enablesmsoff      = parseBoolString(config.get('messages', 'enablesmsoff'))
 enablesmsmovement = parseBoolString(config.get('messages', 'enablesmsmovement'))

 messon            = "\n\n" + personname + " " + ast.literal_eval("'"+config.get('messages', 'messon')+"'")
 messoff           = "\n\n" + personname + " " + ast.literal_eval("'"+config.get('messages', 'messoff')+"'")
 messmovementPre      = ast.literal_eval("'"+config.get('messages', 'messmovement')+"'")

 messmovement = "\n\nOn "+personname+"'s BED" + messmovementPre
# print messmovement
 # Constant Calculations
 maxbuffersize               = int(buffersize) * int(samplingrate)

 elementsNumberOnBed         = onBedTimeWindow * samplingrate

 elementsNumberMovement      = movementTimeWindow * samplingrate

 elementsNumberHR            = hrTimeWindow * samplingrate

 elementsNumberPostureChange =  postureChangeTimeWindow * samplingrate

 # DB Conection
 client = InfluxDBClient(ip, "8086", user, passw, db)
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

 # Infinite Loop
 while True:
    if(debug): print("*****************************************"+str(statusKey))
    stampIni = (datetime.utcfromtimestamp(epoch1).strftime('%Y-%m-%dT%H:%M:%S.000Z'))
    stampEnd = (datetime.utcfromtimestamp(epoch2).strftime('%Y-%m-%dT%H:%M:%S.000Z'))

    if(debug): print(stampIni)
    if(debug): print(stampEnd)
    query = 'SELECT "value" FROM Z WHERE ("location" = \''+unit+'\')  and time >= \''+stampIni+'\' and time <= \''+stampEnd+'\'   '

    result = client.query(query)
    points = list(result.get_points())

    values =  list(map(operator.itemgetter('value'), points))
    times  =  list(map(operator.itemgetter('time'),  points))

    tt = str( values )
    tt = tt.replace(' ', '')

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



# On/Off correlation
    if(statusKey==1):
     if(buffLen>=elementsNumberOnBed and counterTime%timeCheckingOnBed == 0 ):
       signalToOnBed = buffer[buffLen-elementsNumberOnBed:buffLen]

       peaksCR = checkOnBedCR(signalToOnBed,buffertime[len(buffertime)-1])
       nowtime = buffertime[len(buffertime)-1]
       saveResults('corrStatus', 'bs10' ,str(peaksCR), nowtime)
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
       if(counteron > thon):
          #saveON
          if(enablesmson and onBed == False):
             timeDetected = utcToLocalTime(buffertime[len(buffertime)-thon], formatt, from_zone, to_zone)
             subject = subjecton + timeDetected;
             sendEmailT = threading.Thread(target=send_email, args=(companyemail,mailpass,recipients,subject,messon))
             sendEmailT.start()
          saveResults('bedStatus', 'bs' ,'1', buffertime[len(buffertime)-thon])
          onBed = True
          pOnBed = True
       elif(counteroff > thoff):
          if(enablesmsoff and onBed == True):
             timeDetected = utcToLocalTime(buffertime[len(buffertime)-thoff], formatt, from_zone, to_zone)
             subject = subjectoff + timeDetected;
             sendEmailT = threading.Thread(target=send_email, args=(companyemail,mailpass,recipients,subject,messoff))
             sendEmailT.start()
          #saveOFF
          saveResults('bedStatus', 'bs' ,'0', buffertime[len(buffertime)-thoff])
          onBed  = False
          pOnBed = False
          hrSignalNoNoise = 0
       else:
          #Calculing
          saveResults('bedStatus', 'bs' ,'2', buffertime[len(buffertime)-1])
          pOnBed = True

    #################################################################
    #movement
    ################################################################
     if((onBed or pOnBed) and buffLen>=elementsNumberMovement and counterTime%timeCheckingMovement == 0 ):
       movementShowDelay = movementShowDelay + 1
       signalToMovement = buffer[buffLen-elementsNumberMovement:buffLen]
       movement = checkMovement(signalToMovement, movementThreshold, buffertime[len(buffertime)-1], movementShowDelay)
       nowtime = buffertime[len(buffertime)-1]
       if not (movement):
          saveResults('posture', 'x' ,'5', nowtime)
          hrSignalNoNoise = hrSignalNoNoise + timeCheckingMovement
          preMovements.append(0)
       else:
          saveResults('posture', 'x' ,'7', nowtime)

          preMovements.append(1)
          sumMovements = sum(preMovements)
          if(enablesmsmovement and sumMovements > 15):
             timeDetected = utcToLocalTime(buffertime[len(buffertime)-1], formatt, from_zone, to_zone)
             subject = subjectmovement + timeDetected;
             sendEmailT = threading.Thread(target=send_email, args=(companyemail,mailpass,recipients,subject,messmovement))
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
#        hbr = calculateHBR(signalToHBR, lowCut, highCut, samplingrate, order, buffertime[len(buffertime)-1])
#        hbr = calculateHBR2(signalToHBR, fm, eigs, dpss, nfft, buffertime[len(buffertime)-1])
        signalFiltered = butter_bandpass_filter(signalToHBR, lowCut, highCut, samplingrate, order)
        hbr,rr = calculateHBR3(signalFiltered, fm, eigs, dpss, nfft, buffertime[len(buffertime)-1],mpdEnv)
        nowtime = buffertime[len(buffertime)-1]
        saveResults('hrate', 'hr' ,str(hbr), nowtime)
        saveResults('rrate', 'rr' ,str(rr), nowtime)
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
       percent = calculatePostureChange(previousHBSignal, currentHBSignal, buffertime[len(buffertime)-1])
       nowtime = buffertime[len(buffertime)-1]
       saveResults('change', 'x' ,str(percent), nowtime)
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
    if(counterTime%30 == 0):
       if(debug): print("-----------------------------------------------------------------------")
       config = configparser.ConfigParser()
       openCF = open(r'./conf/config.sys')
       config.read_file(openCF)

       personname        = config.get('messages', 'personname')
       recipients        = ast.literal_eval(config.get('messages', 'recipients'))
       enablesmson       = parseBoolString(config.get('messages', 'enablesmson'))
       enablesmsoff      = parseBoolString(config.get('messages', 'enablesmsoff'))
       enablesmsmovement = parseBoolString(config.get('messages', 'enablesmsmovement'))
       thccMean          = float(config.get('main', 'thccMean'))
       mpdEnv            = int(config.get('main', 'mpdEnv'))
       if(debug): print(thccMean)
       if(debug): print(mpdEnv)
       messmovement = "\n\nOn "+personname+"'s BED" + messmovementPre
       messon            = "\n\n" + personname + " " + ast.literal_eval("'"+config.get('messages', 'messon')+"'")
       messoff           = "\n\n" + personname + " " + ast.literal_eval("'"+config.get('messages', 'messoff')+"'")

       openCF.close()
       statusKey  = status()

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
