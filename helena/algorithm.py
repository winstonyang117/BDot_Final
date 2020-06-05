import chardet
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
import ConfigParser
import sys
import logging
from detect_peaks import detect_peaks
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
import statsmodels.api as sm
#import netifaces
import json
import requests

# Bandpass filter functions
def butter_bandpass(lowcut, highcut, fs, order):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = lfilter(b, a, data)
    return y

def butter_bandstop_filter(data, lowcut, highcut, fs, order):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq

        i, u = butter(order, [low, high], btype='bandstop')
        y = lfilter(i, u, data)
        return y
# OnBed function

def checkOnBedCR(signal,time):
#       arrSignal = array( signal )
       signalFiltered = butter_bandstop_filter(signal, 17 , 22 , 100, 5)
       arrSignal = array( signalFiltered )
       auto = sm.tsa.stattools.acf(arrSignal, unbiased=False, nlags=100, qstat=False, fft=None)

       peaks = detect_peaks(auto, show=False)
       correpk = len(peaks)
       saveResults('corrStatus', 'bs10' ,str(correpk), time)

       return correpk


def checkOnBed(signal, onBedThreshold, lowCut, highCut, fs, order, time):
    signalFiltered = butter_bandpass_filter(signal, lowCut, highCut, fs, order)
    maxValue = max(signalFiltered)
#    print maxValue
    log = "./componets/logs/onbed.log"
    logging.basicConfig(filename=log,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    
    if(maxValue > onBedThreshold):
       # Save Info# Status 2 --> may on Bed
       saveResults('bedStatus', 'bs' ,'2', time)
       logging.info(str(maxValue)+' True')
       return True
    else:
       # Save Info# Status o --> off Bed
       #saveResults('bedStatus', 'bs' ,'0', time)
       #logging.info(str(maxValue)+' False')
       return False

# OnBed new Features
def checkOnBedNF(signal, lowCut, highCut, fs, order):
       signalFiltered = butter_bandpass_filter(signal, lowCut, highCut, fs, order)
       kur2 = kurtosis(signalFiltered,fisher = False)

       df = list(numpy.diff(signalFiltered))
       df[:0] = [0]
       squ = numpy.square(df[1:len(df)-1])
       oddi = df[0:len(df)-2]
       eveni = df[2:len(df)]
       ey = squ - numpy.multiply(oddi,eveni)
       meanop1 = numpy.mean(ey)/100000

       ratio = kur2 / meanop1 ;
       return ratio


# Movement fuction
def checkMovement(signal, movementThreshold, time, movementShowDelay):
    log = "./componets/logs/movement.log"
    logging.basicConfig(filename=log,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    signal.sort(reverse = True)
    if(signal[0]>movementThreshold and signal[1]>movementThreshold):
       saveResults('posture', 'x' ,'7', time)
       logging.info(str(signal[0])+' - '+str(signal[1])+' True')
       return True
    else:
       if(movementShowDelay==5):
          saveResults('posture', 'x' ,'5', time)
       logging.info(str(signal[0])+' - '+str(signal[1])+' False')
       return False

# HearthbeatRate function
def calculateHBR(signal, lowCut, highCut, fs, order, time):

    mean = reduce(lambda x, y: x + y, signal) / len(signal)
    signal[:] = [x - mean for x in signal]
    signalFiltered = butter_bandpass_filter(signal, lowCut, highCut, fs, order)

    peaks = detect_peaks(signalFiltered, mpd=60, show=False)
    hbr = len(peaks)*2
#    if(debug): print '----------------------------------'+str(hbr)
    div = float(random.randint(40,42)/10.0)
    rr = float(hbr/div)
    saveResults('hrate', 'hr' ,str(hbr), time)
    saveResults('rrate', 'rr' ,str(rr), time)
    return hbr

def calculateHBR2(signal, fm, eigs, dpss, nfft, time):
    ss = array( signal )
    xk = nt_alg.tapered_spectra(ss, dpss, NFFT=nfft)
       
    mtm_bband = np.abs( np.sum( 2 * (xk[:,fm] * np.sqrt(eigs))[:,None] * dpss, axis=0 ) )
    peaks = detect_peaks(mtm_bband, mpd=45, show=False)
    hbr = len(peaks)*2

#   RR

    values = np.zeros((1,len(peaks)))
    cValues = 0;
    for val in peaks:
           values[0,cValues] = mtm_bband[val]
           cValues = cValues + 1
    values = values.ravel()
    xvals = np.linspace(0, 3000, 300)

    Srr = sp.interpolate.interp1d(peaks,values, kind='cubic',bounds_error=False)(xvals)


    peaks = detect_peaks(Srr, mpd=20, show=False)

    breCount = len(peaks)
    distance = 0
    for i in range (0,breCount-1):
          distance = distance + (peaks[i+1]-peaks[i])
    
    rr =  600.0 / (distance / (breCount-1))

    #print hbr
    #print rr
    saveResults('hrate', 'hr' ,str(hbr), time)
    saveResults('rrate', 'rr' ,str(rr), time)
    return hbr

def calculateHBR3(signal, fm, eigs, dpss, nfft, time, mpdEnv):
    # 25 got apple watch 23 good for high HR
    peaks = detect_peaks(signal, mpd=mpdEnv, edge = 'both' , show=False)

    values = np.zeros((1,len(peaks)))
    cValues = 0;
    for val in peaks:
         values[0,cValues] = signal[val]
         cValues = cValues + 1
    values = values.ravel()

       
    xvals = np.linspace(0, 3000, 3000)
    hri = sp.interpolate.interp1d(peaks,values, kind='cubic',bounds_error=False)(xvals)
    peaks = detect_peaks(hri, mpd=45, show=False)
    hbr = len(peaks)*2

#RR
    values = np.zeros((1,len(peaks)))
    cValues = 0;
    for val in peaks:
           values[0,cValues] = hri[val]
           cValues = cValues + 1
    values = values.ravel()
    xvals = np.linspace(0, 3000, 300)

    Srr = sp.interpolate.interp1d(peaks,values, kind='cubic',bounds_error=False)(xvals)


    peaks = detect_peaks(Srr, mpd=20, show=False)

#    print peaks
    breCount = len(peaks)
    distance = 0
    for i in range (0,breCount-1):
          distance = distance + (peaks[i+1]-peaks[i])

#    print distance    
    rr =  600.0 / (distance / (breCount-1))

    #print hbr
    #print rr
    saveResults('hrate', 'hr' ,str(hbr), time)
    saveResults('rrate', 'rr' ,str(rr), time)

    return hbr

# Posture Change function
def calculatePostureChange(previousHBSignal, currentHBSignal, time):

    f, current  = signal.welch(currentHBSignal, nperseg=100, noverlap = 50, fs=100)
    f, previous = signal.welch(previousHBSignal, nperseg=100, noverlap = 50, fs=100)
    # Calculate
    res = numpy.corrcoef(previous , current)
    percent = res[0][1]


    # print "Posture Change",percent 

    saveResults('change', 'x' ,str(percent), time)
#    return hbr
