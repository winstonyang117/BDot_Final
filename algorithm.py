from __future__ import division, print_function
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
import random import randint
import time
import operator
import ConfigParser
import sys
import logging
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

# OnBed function

def checkOnBedCR(signal,time):
        return 10

# Movement fuction
def checkMovement(signal, movementThreshold, time, movementShowDelay):
    if (randint(0,10) > 5)
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
