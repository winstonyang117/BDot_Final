
import chardet
import urllib3
import netifaces
from scipy.signal import butter, lfilter
from scipy import signal
from datetime import datetime, date
from random import randint
import time
import operator
import sys
import logging
import numpy as np
import scipy as sp
import ast
import json


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

# OnBed function

def checkOnBedCR(signal,time):
        return randint(5,30)

# Movement fuction
def checkMovement(signal, movementThreshold, time, movementShowDelay):
    if (randint(0,10) > 5):
        return True
    else:
        return False
# HearthbeatRate function

def calculateHBR3(signal, fm, eigs, dpss, nfft, time, mpdEnv):
    return randint(60,90), randint(10,20);

# Posture Change function
def calculatePostureChange(previousHBSignal, currentHBSignal, time):
    return 0.8
#    return hbr
