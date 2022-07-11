#!/usr/bin/env python3

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
# import algorithm as alg
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
import subprocess
from dateutil.parser import parse

# from glm_alg import GLM_Model
# from RF_alg import RF_Model
from dl_alg import DL_Model
import algorithm as dsp

#from config import Config
import webbrowser
from util import local_time_epoch
from util import write_influx
import warnings
warnings.filterwarnings("ignore")

def utcToLocalTime(time2, formatt, from_zone, to_zone):
    utc = datetime.strptime(time2, formatt)
    utc = utc.replace(tzinfo=from_zone)
    central = utc.astimezone(to_zone)
    timeDetected = central.strftime("%m-%d %I:%M %p")
    return timeDetected

def str2bool(v):
  return v.lower() in ("true", "1", "https", "t")

# ip = "sensorweb.us"
# port = "8086"
# user = "test"
# passw = "sensorweb"
# db = "shake"

# ip = "homedots.us"
# port = "8086"
# user = "test"
# passw = "homedots"
# db = "shake"

# rip = ip
debug = True; #str2bool(config.get('general', 'debug'))
verbose = True
formatt = '%Y-%m-%dT%H:%M:%S.%fZ'
from_zone = tz.tzutc()
to_zone = pytz.timezone("America/New_York")

src = {'ip': 'https://homedots.us', 'port': '8086', 'db': 'shake', 'user':'test', 'passw':'homedots'}
dst = {'ip': 'https://homedots.us', 'port': '8086', 'db': 'healthresult', 'user':'beddot', 'passw':'HDots2020'}
# dest = {'ip': 'https://sensorweb.us', 'db': 'algtest', 'user':'test', 'passw':'sensorweb'}

# def saveResults(unit, serie, field, value, time):
#    time = time[0:19]

#    utc_time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S")
#    epoch_time = utc_time.timestamp() #int((utc_time - datetime(1970, 1, 1)).total_seconds())

#    http_post2 = "curl -s -POST --insecure \'https://"+rip+":"+rport+"/write?db="+rdb+"\' -u "+ruser+":"+rpassw+" --data-binary \' "
#    http_post2 += "\n"+serie+",location="+unit+" "+field+"="+value+" "+str(epoch_time)+"000000000"
#    http_post2 += "\'  &"

#    subprocess.call(http_post2, shell=True)



########### main entrance ########
def main():
    progname = sys.argv[0]
    if(len(sys.argv)<2):
        print("Usage: %s mac [start] [end] [ip] [https/http]" %(progname))
        print("Example: %s b8:27:eb:97:f5:ac   # start with current time and run in real-time as if in a node" %(progname))
        print("Example: %s b8:27:eb:97:f5:ac 2020-08-13T02:03:00.200 # start with the specified time and run non-stop" %(progname))
        print("Example: %s b8:27:eb:97:f5:ac 2020-08-13T02:03:00.200 2020-08-13T02:05:00.030 # start and end with the specified time" %(progname))
        print("Example: %s b8:27:eb:97:f5:ac 2020-08-13T02:03:00.200 2020-08-13T02:05:00.030 sensorweb.us https # specify influxdb IP and http/https" %(progname))
        quit()

#  formatt = '%Y-%m-%dT%H:%M:%S.%fZ'
#  from_zone = tz.tzutc()
#  to_zone = pytz.timezone("America/New_York")

    # Parameters from Config file
    db           = 'shake' # config.get('general', 'dbraw')
    buffersize   = 60 # config.get('general', 'buffersize')
    samplingrate = 100 # int(config.get('general', 'samplingrate'))
    hrTimeWindow    = 30 # int(config.get('main', 'hrTimeWindow'))
    maxbuffersize               = int(buffersize) * int(samplingrate)
    windowSize = elementsNumberHR = hrTimeWindow * samplingrate

    # Buffers for time and
    buffer      = []
    buffertime  = []

    # Parameters from Config file
    db           = 'shake' # config.get('general', 'dbraw')
    buffersize   = 60 # config.get('general', 'buffersize')
    samplingrate = 100 # int(config.get('general', 'samplingrate'))
    hrTimeWindow    = 30 # int(config.get('main', 'hrTimeWindow'))
    maxbuffersize               = int(buffersize) * int(samplingrate)
    windowSize = elementsNumberHR = hrTimeWindow * samplingrate

# Bed occupancy, movement and posture related variables

    # Parameters for Component 1 --> OnBed
    #seconds
    onBedTimeWindow = 3 #int(config.get('main', 'onBedTimeWindow'))
    lowCut = 0.7 #float(config.get('main', 'lowCut'))
    highCut = 8 #float(config.get('main', 'highCut'))
    order = 4 #int(config.get('main', 'order'))
    onBedThreshold = 9000 #int(config.get('main', 'onBedThreshold'))
    timeCheckingOnBed = 1 #int(config.get('main', 'timeCheckingOnBed'))
    # 1.5
    thratio = 1.5 #float(config.get('main', 'ratioThreshold'))
    #0.5
    thsd = 0.5 #float(config.get('main', 'sdThreshold')) # sdThreshold = 0.5
    #35
    thon  = 30 #12 #20 # 44 # int(config.get('main', 'secondsForOn'))
    thoff = 30 #12 #20 # 55 #int(config.get('main', 'secondForOff'))

    thccMean = 12 #float(config.get('main', 'thccMean'))
    mpdEnv = 20 #int(config.get('main', 'mpdEnv'))

    # check large energy events
    indexEnergy = 0
    maxEnergy = 0
    energyWindow = 30 # there should be a large events with energyWindow = thon and thoff seconds
    energyThreshold = 10000
    energyList = np.zeros(energyWindow)

    # Parameters for Component 2 --> Movement
    #seconds
    movementTimeWindow = 1 #int(config.get('main', 'movementTimeWindow'))
    timeCheckingMovement = 1 #int(config.get('main', 'timeCheckingMovement'))
    movementThreshold = 400000 #int(config.get('main', 'movementThreshold')) 

    # Parameters for Component 3 --> HeartbeatRate
    #seconds
    hrTimeWindow    = 30 #int(config.get('main', 'hrTimeWindow'))
    timeCheckingHR  = 3 #int(config.get('main', 'timeCheckingHR'))

    # Parameters for Component 4 --> Posture Change
    #seconds
    postureChangeTimeWindow = 5 #int(config.get('main', 'postureChangeTimeWindow'))

    # Parameters for alert settings
    enablesmson       = True #parseBoolString(config.get('messages', 'enablesmson'))
    enablesmsoff      = True #parseBoolString(config.get('messages', 'enablesmsoff'))
    enablesmsmovement = True #parseBoolString(config.get('messages', 'enablesmsmovement'))
        
    elementsNumberOnBed         = onBedTimeWindow * samplingrate
    elementsNumberMovement      = movementTimeWindow * samplingrate
    elementsNumberHR            = hrTimeWindow * samplingrate
    elementsNumberPostureChange =  postureChangeTimeWindow * samplingrate
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
    # counterFalseOnBed
    counterFalseOnBed = 0
    counteron  = 0
    counteroff = 0
    prevalues = []
    preMovements = []
    pOnBed = False
    sumMovements = 0
    # posture change related parameters
    previousHBSignal = []
    currentHBSignal  = []

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


#t1 = time.perf_counter()
#print("t1-t0= " +str(t1-t0))
    dsp.logpath = ""
# Getting the user input parameters
#  global ip, rip

    unit = sys.argv[1]

    if(len(sys.argv) > 4):
        src['ip'] = sys.argv[4] # influxdb IP address
        dst['ip'] = sys.argv[4]

    if(len(sys.argv) > 5):
        ssl = str2bool(sys.argv[5]) #https or http
        httpStr = "http://"
    else:
        ssl = True
        httpStr = "https://"

    if(len(sys.argv) > 2):
        # current = datetime.strptime(sys.argv[2], "%Y-%m-%dT%H:%M:%S.%fZ") + (datetime.utcnow() - datetime.now())
    #    current = datetime.strptime("2018-06-29T08:15:27.243860Z", "%Y-%m-%dT%H:%M:%S.%fZ")
        current = local_time_epoch(sys.argv[2], "America/New_York")

    else:
        current = datetime.now().timestamp()
        bDependOnMovement = True

    if(len(sys.argv) > 3):
        endSet = True
    #     end = datetime.strptime('2018-06-29T08:15:27.243860', '%Y-%m-%dT%H:%M:%S.%f')
        #  end = datetime.strptime(sys.argv[3], "%Y-%m-%dT%H:%M:%S.%fZ") + (datetime.utcnow() - datetime.now())
        end = local_time_epoch(sys.argv[3], "America/New_York")
    else:
        endSet = False
        end = datetime.now().timestamp() # never will be used, just give a value to avoid compile errors

    endEpoch = end # int( (end - datetime(1970,1,1)).total_seconds())

    # Determining the starting point of the buffer using epoch time
    epoch2 = current # int( (current - datetime(1970,1,1)).total_seconds())
    startEpoch = epoch2

 #current = datetime.utcnow()
#  print("len(sys.argv)", len(sys.argv))
#  print("### Current time:", current, " ### \n")
#  print("### End time:", end, " ### \n")
#  print("Click here to see the results in Grafana:\n\n" +
#               httpStr + rip + ":3000/d/o2RBARGMz/bed-dashboard-algtest?var-mac=" +
#                str(unit)+ "&orgId=1&from=" + str(startEpoch) + "000" + "&to=" + str(endEpoch) + "000")

    print("len(sys.argv)", len(sys.argv))
    print("### Current time:", current, " ### \n")
    print("### End time:", end, " ### \n")
    url = dst['ip'] + ":3000/grafana/d/o2RBARGMz/bed-dashboard-algtest?var-mac=" + str(unit)

    if(len(sys.argv) > 2):
        url = url + "&from=" + str(int(startEpoch*1000)) #+ "000"
    else:
        url = url + "&from=now-2m"

    if(len(sys.argv) > 3):
        url = url + "&to=" + str(int(endEpoch*1000)) #+ "000"
    else:
        url = url + "&to=now"
    url = url + "&orgId=1&refresh=3s"


    print("Click here to see the results in Grafana:\n\n" + url)
    #  input("Press any key to continue")
    webbrowser.open(url, new=2)


    # Parameters for the Query
    epoch2 = epoch2 - 1
    epoch1 = epoch2 - 1

    try:
        client = InfluxDBClient(src['ip'].split('//')[1], src['port'], src['user'], src['passw'], src['db'], ssl)
    #    client = InfluxDBClient(ip, port, user, passw, db, ssl)
    except Exception as e:
        print("main(), DB access error:")
        print("Error", e)
        quit()


    # set max retries for DB query
    numTry = 0
    MAXTRY = 100 # max try of 100 seconds
    result = []
    # Infinite Loop

    #### declare model here
    #  alg = GLM_Model()
    #  alg.load_model(f'../models/glm.pickle')

    #  alg = RF_Model()
    #  alg.load_model(f'../models/RF.pickle')

    alg = DL_Model()
    alg.load_model('../models/DL_net_model/')

    last_predictions = [0,0]
    smooth_list = []
    smooth_index = 60

    counterTime = 0
    while True:
        # Cheking is the process need to sleep
        current = datetime.now().timestamp() #(datetime.utcnow() - datetime(1970,1,1)).total_seconds()
        epoch2 = epoch2 + 1
        epoch1 = epoch1 + 1
        if (endSet == False and (current-epoch2) < 1):
            time.sleep(1)
            if(debug): print("*********")

    #    if(debug): print("*****************************************"+str(statusKey))
        if (endSet and epoch2 > endEpoch):
            if(debug): print("**** Ended as ", epoch2, " > ", end, " ***")
            print("Click here to see the results in Grafana:\n\n" + url)
            # print("Click here to see the results in Grafana:\n\n" +
            #       httpStr + rip + ":3000/d/o2RBARGMz/bed-dashboard-algtest?var-mac=" +
            #        str(unit)+ "&orgId=1&from=" + str(int(startEpoch*1000)) + "&to=" + str(int(endEpoch*1000)) )
            #print("The sleep monitoring result from node program is at https://sensorweb.us:3000/d/VmjKXrXWz/bed-dashboard?orgId=1&refresh=5s&var-mac=" + str(unit))
            quit()

        # stampIni = (datetime.utcfromtimestamp(epoch1).strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
        # stampEnd = (datetime.utcfromtimestamp(epoch2).strftime('%Y-%m-%dT%H:%M:%S.%fZ'))
        #t0 = time.perf_counter()
        # if(debug): print("stampIni time: " + stampIni)
        # if(debug): print("stampEnd time: " + stampEnd)
        # query = 'SELECT "value" FROM Z WHERE ("location" = \''+unit+'\')  and time >= \''+stampIni+'\' and time <= \''+stampEnd+'\'   '
        print('start:', epoch1, 'end:', epoch2)
        query = 'SELECT "value" FROM Z WHERE ("location" = \''+unit+'\')  and time >= '+ str(int(epoch1*10e8))+' and time <= '+str(int(epoch2*10e8))
        print(query)

        try:
            result = client.query(query)
        except Exception as e:
            print("main(), no data in the query time period:")
            print("Error", e)
            time.sleep(1)
            numTry += 1
            if (numTry > MAXTRY):
                quit()

        # print(result)
        points = list(result.get_points())
        values =  list(map(operator.itemgetter('value'), points))
        times  =  list(map(operator.itemgetter('time'),  points))

        # the buffer management modules
        buffertime = buffertime + times
        buffer     = buffer + values
        buffLen    = len(buffer)
        if(debug):
            print("buffLen: ", buffLen)
            if(buffLen>0):
                print("Buffer Time:    " + str(buffertime[0]) + "  -   " + str(buffertime[buffLen-1]))

        # Cutting the buffer when overflow
        if(buffLen > maxbuffersize):
            difSize = buffLen - maxbuffersize
            del buffer[0:difSize]
            del buffertime[0:difSize]
            buffLen    = buffLen - difSize
        # get more data if the buffer does not have enough data for the minimum window size
        if (buffLen < windowSize):
            continue

        data = buffer[buffLen-windowSize:buffLen]
        nowtime = buffertime[buffLen-1]

        #  the blood pressure estimation algorithm
        if(debug): print("Calculating vital signs")

        ### add my code here
        # On/Off correlation
        if(buffLen>=elementsNumberOnBed and counterTime%timeCheckingOnBed == 0 ):
        #t2 = time.perf_counter()

            signalToOnBed = buffer[buffLen-elementsNumberOnBed:buffLen]

            peaksCR = dsp.checkOnBedCR(signalToOnBed,buffertime[len(buffertime)-1])
            nowtime = buffertime[len(buffertime)-1]

        #    saveResults('corrStatus', 'bs10' ,str(peaksCR), nowtime, config)
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
            # if(debug):
            if(debug): print(" Peaks:", peaksCR, " Mean:", ccMean, " On:", counteron, " Off:", counteroff)
        
        # edited by Song on 10/20/2020 to add check of maxEnergy
        #if(counteron > thon and maxEnergy > energyThreshold):
            if(counteron > thon):
        # end edit by Song on 10/20/2020
            #saveON
                if(enablesmson and onBed == False):
                    timeDetected = utcToLocalTime(buffertime[len(buffertime)-thon], formatt, from_zone, to_zone)
                    # sendEmailT = threading.Thread(target=send_alert, args=(alert_url, 1))
                    # sendEmailT.start()
                # saveResults('bedStatus', 'bs' ,'1', buffertime[len(buffertime)-thon], config)
                timestamp = local_time_epoch(nowtime[:-1], "UTC")
                # write_influx(dst, unit, 'bedStatus', 'bs', '1', timestamp, 1)
                onBed = True
                pOnBed = True
        # edited by Song on 10/20/2020 to add check of maxEnergy
        #  elif(counteroff > thoff and maxEnergy > energyThreshold):
            elif(counteroff > thoff):
        # end edit by Song on 10/20/2020
                if(enablesmsoff and onBed == True):
                    timeDetected = utcToLocalTime(buffertime[len(buffertime)-thoff], formatt, from_zone, to_zone)
                    # sendEmailT = threading.Thread(target=send_alert, args=(alert_url, 2))
                    # sendEmailT.start()
            #saveOFF
                # saveResults('bedStatus', 'bs' ,'0', buffertime[len(buffertime)-thoff], config)
                timestamp = local_time_epoch(nowtime[:-1], "UTC")
                # write_influx(dst, unit, 'bedStatus', 'bs', '0', timestamp, 1)
                onBed  = False
                pOnBed = False
                hrSignalNoNoise = 0
            else:
            #Calculing
            # removed by Song on 10/16/2020
            #  saveResults('bedStatus', 'bs' ,'2', buffertime[len(buffertime)-1], config)
                if(onBed):
                    # saveResults('bedStatus', 'bs' ,'1', buffertime[len(buffertime)-1], config)
                    timestamp = local_time_epoch(nowtime[:-1], "UTC")
                    # write_influx(dst, unit, 'bedStatus', 'bs', '1', timestamp, 1)
                else:
                    # saveResults('bedStatus', 'bs' ,'0', buffertime[len(buffertime)-1], config)
                    timestamp = local_time_epoch(nowtime[:-1], "UTC")
                    # write_influx(dst, unit, 'bedStatus', 'bs', '0', timestamp, 1)
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
                    timestamp = local_time_epoch(nowtime[:-1], "UTC")
                    # write_influx(dst, unit, 'posture', 'x', '5', timestamp, 1)

                    hrSignalNoNoise = hrSignalNoNoise + timeCheckingMovement
                    preMovements.append(0)
                else:
                    # saveResults('posture', 'x' ,'7', nowtime, config)
                    timestamp = local_time_epoch(nowtime[:-1], "UTC")
                    # write_influx(dst, unit, 'posture', 'x', '7', timestamp, 1)

                    preMovements.append(1)
                    sumMovements = sum(preMovements)
                    if(enablesmsmovement and sumMovements > 15):
                        timeDetected = utcToLocalTime(buffertime[len(buffertime)-1], formatt, from_zone, to_zone)
                        # sendEmailT = threading.Thread(target=send_alert, args=(alert_url, 3))
                        #sendEmailT = threading.Thread(target=send_email, args=(companyemail,mailpass,recipients,subject,messmovement))
                        # sendEmailT.start()
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
                signalToHBR = buffer[buffLen-elementsNumberHR:buffLen]
                nowtime = buffertime[len(buffertime)-1]

                [bph, bpl] = alg.predict(np.asarray(signalToHBR))
                bph = [bph] # for making it a list to wirte into influx
                bpl = [bpl]
                # import pdb; pdb.set_trace()

                if [bph, bpl] == [None, None]:
                    [bph, bpl] = last_predictions
                    if last_predictions == [0,0]: continue
                else:
                    last_predictions = [bph, bpl]

                if(debug): print(' bph:', bph, ' bpl:', bpl)
                print('nowtime:', nowtime)
                timestamp = local_time_epoch(nowtime[:-1], "UTC")
                write_influx(dst, unit, 'vitalsigns', 'systolic', bph, timestamp, 1)
                write_influx(dst, unit, 'vitalsigns', 'diastolic', bpl, timestamp, 1)
        #        hbr = alg.calculateHBR(signalToHBR, lowCut, highCut, samplingrate, order, buffertime[len(buffertime)-1])
        #        hbr = alg.calculateHBR2(signalToHBR, fm, eigs, dpss, nfft, buffertime[len(buffertime)-1])
                # signalFiltered = alg.butter_bandpass_filter(signalToHBR, lowCut, highCut, samplingrate, order)
                # hbr,rr = alg.calculateHBR3(signalFiltered, fm, eigs, dpss, nfft, buffertime[len(buffertime)-1],mpdEnv)

                # saveResults('hrate', 'hr' ,str(hbr), nowtime, config)
                # saveResults('rrate', 'rr' ,str(rr), nowtime, config)
        #         if(hbr > 30):
        # #            if(debug): print "HBR greater than 30 --> ",hbr
        #             previousHBSignal = buffer[buffLen-elementsNumberPostureChange:buffLen]
        
        counterTime = counterTime + 1

        # end of while
    # end of main

if __name__== '__main__':
  main()
