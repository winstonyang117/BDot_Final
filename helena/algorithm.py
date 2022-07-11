import chardet
from scipy.signal import butter, lfilter
from scipy import signal
from datetime import datetime, date
import numpy
import random
import time
import sys
import logging
#from detect_peaks import detect_peaks
from scipy.stats import kurtosis
import nitime.algorithms as nt_alg
import numpy as np
from numpy import array
import scipy as sp
import ast
from statsmodels.tsa.stattools import acf
#import statsmodels.api.tsa.stattools as stattools
#import componets.saveResults as SaveToDB

#def saveResults(serie, field, value, time):
#    SaveToDB.saveResults(serie, field, value, time)
logpath = "/opt/helena/logs/"
#logpath = ""

def detect_peaks(x, mph=None, mpd=1, threshold=0, edge='rising',
                 kpsh=False, valley=False, show=False, ax=None):

    x = np.atleast_1d(x).astype('float64')
    if x.size < 3:
        return np.array([], dtype=int)
    if valley:
        x = -x
        if mph is not None:
            mph = -mph
    # find indices of all peaks
    dx = x[1:] - x[:-1]
    # handle NaN's
    indnan = np.where(np.isnan(x))[0]
    if indnan.size:
        x[indnan] = np.inf
        dx[np.where(np.isnan(dx))[0]] = np.inf
    ine, ire, ife = np.array([[], [], []], dtype=int)
    if not edge:
        ine = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) > 0))[0]
    else:
        if edge.lower() in ['rising', 'both']:
            ire = np.where((np.hstack((dx, 0)) <= 0) & (np.hstack((0, dx)) > 0))[0]
        if edge.lower() in ['falling', 'both']:
            ife = np.where((np.hstack((dx, 0)) < 0) & (np.hstack((0, dx)) >= 0))[0]
    ind = np.unique(np.hstack((ine, ire, ife)))
    # handle NaN's
    if ind.size and indnan.size:
        # NaN's and values close to NaN's cannot be peaks
        ind = ind[np.in1d(ind, np.unique(np.hstack((indnan, indnan-1, indnan+1))), invert=True)]
    # first and last values of x cannot be peaks
    if ind.size and ind[0] == 0:
        ind = ind[1:]
    if ind.size and ind[-1] == x.size-1:
        ind = ind[:-1]
    # remove peaks < minimum peak height
    if ind.size and mph is not None:
        ind = ind[x[ind] >= mph]
    # remove peaks - neighbors < threshold
    if ind.size and threshold > 0:
        dx = np.min(np.vstack([x[ind]-x[ind-1], x[ind]-x[ind+1]]), axis=0)
        ind = np.delete(ind, np.where(dx < threshold)[0])
    # detect small peaks closer than minimum peak distance
    if ind.size and mpd > 1:
        ind = ind[np.argsort(x[ind])][::-1]  # sort ind by peak height
        idel = np.zeros(ind.size, dtype=bool)
        for i in range(ind.size):
            if not idel[i]:
                # keep peaks with the same height if kpsh is True
                idel = idel | (ind >= ind[i] - mpd) & (ind <= ind[i] + mpd) \
                    & (x[ind[i]] > x[ind] if kpsh else True)
                idel[i] = 0  # Keep current peak
        # remove the small peaks and sort back the indices by their occurrence
        ind = np.sort(ind[~idel])

    # if show:
    #     if indnan.size:
    #         x[indnan] = np.nan
    #     if valley:
    #         x = -x
    #         if mph is not None:
    #             mph = -mph
    #     _plot(x, mph, mpd, threshold, edge, valley, ax, ind)

    return ind


# def _plot(x, mph, mpd, threshold, edge, valley, ax, ind):
#     """Plot results of the detect_peaks function, see its help."""
#     try:
#         import matplotlib.pyplot as plt
#     except ImportError:
#         print('matplotlib is not available.')
#     else:
#         if ax is None:
#             _, ax = plt.subplots(1, 1, figsize=(8, 4))

#         ax.plot(x, 'b', lw=1)
#         if ind.size:
#             label = 'valley' if valley else 'peak'
#             label = label + 's' if ind.size > 1 else label
#             ax.plot(ind, x[ind], '+', mfc=None, mec='r', mew=2, ms=8,
#                     label='%d %s' % (ind.size, label))
#             ax.legend(loc='best', framealpha=.5, numpoints=1)
#         ax.set_xlim(-.02*x.size, x.size*1.02-1)
#         ymin, ymax = x[np.isfinite(x)].min(), x[np.isfinite(x)].max()
#         yrange = ymax - ymin if ymax > ymin else 1
#         ax.set_ylim(ymin - 0.1*yrange, ymax + 0.1*yrange)
#         ax.set_xlabel('Data #', fontsize=14)
#         ax.set_ylabel('Amplitude', fontsize=14)
#         mode = 'Valley detection' if valley else 'Peak detection'
#         ax.set_title("%s (mph=%s, mpd=%d, threshold=%s, edge='%s')"
#                      % (mode, str(mph), mpd, str(threshold), edge))
#         # plt.grid()
#         plt.show()

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
       auto = acf(arrSignal, unbiased=False, nlags=100, qstat=False, fft=None)

       peaks = detect_peaks(auto, show=False)
       correpk = len(peaks)
       #saveResults('corrStatus', 'bs10' ,str(correpk), time)

       return correpk


def checkOnBed(signal, onBedThreshold, lowCut, highCut, fs, order, time):
    signalFiltered = butter_bandpass_filter(signal, lowCut, highCut, fs, order)
    maxValue = max(signalFiltered)
#    print maxValue
    log = logpath + "onbed.log"
    logging.basicConfig(filename=log,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')

    if(maxValue > onBedThreshold):
       # Save Info# Status 2 --> may on Bed
       #saveResults('bedStatus', 'bs' ,'2', time)
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
    log = logpath +  "movement.log"
    logging.basicConfig(filename=log,level=logging.DEBUG,format='%(asctime)s %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
    signal.sort(reverse = True)
    if(signal[0]>movementThreshold and signal[1]>movementThreshold):
       #saveResults('posture', 'x' ,'7', time)
       logging.info(str(signal[0])+' - '+str(signal[1])+' True')
       return True
    else:
       #if(movementShowDelay==5):
       #   saveResults('posture', 'x' ,'5', time)
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
    #saveResults('hrate', 'hr' ,str(hbr), time)
    #saveResults('rrate', 'rr' ,str(rr), time)
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
    #saveResults('hrate', 'hr' ,str(hbr), time)
    #saveResults('rrate', 'rr' ,str(rr), time)
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
    #saveResults('hrate', 'hr' ,str(hbr), time)
    #saveResults('rrate', 'rr' ,str(rr), time)

    return hbr, rr

# Posture Change function
def calculatePostureChange(previousHBSignal, currentHBSignal, time):

    f, current  = signal.welch(currentHBSignal, nperseg=100, noverlap = 50, fs=100)
    f, previous = signal.welch(previousHBSignal, nperseg=100, noverlap = 50, fs=100)
    # Calculate
    res = numpy.corrcoef(previous , current)
    percent = res[0][1]


    # print "Posture Change",percent

    # saveResults('change', 'x' ,str(percent), time)
    return percent


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def calculateBP_v2(signal, fs, cutoff,nlags,order):

    signalFiltered = butter_lowpass_filter(sigs, cutoff, fs, order)

    arrSignal = array( signalFiltered )
    auto = sm.tsa.stattools.acf(arrSignal, unbiased=False, nlags=nlags,qstat=False)
    peaks = detect_peaks(auto,show=False)

    bp1=(976.35,0,0,427.48,0,-1148.9,-2094.9,535.67)
    bp11=(0,0,0,0,0,1503.6)
    bp12=(0,0,0,0,-488.87)
    bp13=(0,0,0,0)
    bp14=(0,0,-100.64)
    bp15=(2657.5,-1182.4)
    bp16=(206.17)

    bp2=(-31.933,0,0,-912.89,0,-11870,8201.5,2095.8)
    bp21=(0,0,0,0,0,-6.9995)
    bp22=(0,0,0,0,676.65)
    bp23=(0,0,0,0)
    bp24=(0,0,1130.8)
    bp25=(3801.5,8920.9)
    bp26=(-11246)

    bptt1 = peaks[0:7]/fs
    bptt11 = bptt1[0]*bptt1[1:7]
    bptt12 = bptt1[1]*bptt1[2:7]
    bptt13 = bptt1[2]*bptt1[3:7]
    bptt14 = bptt1[3]*bptt1[4:7]
    bptt15 = bptt1[4]*bptt1[5:7]
    bptt16 = bptt1[5]*bptt1[6:7]

    bpttlow = bp1[1:8]
    bptthigh = bp2[1:8]


    bplow =np.ceil(np.absolute(np.dot(bptt1,bpttlow)+np.dot(bptt11,bp11)+np.dot(bptt12,bp12)+np.dot(bptt13,bp13)+np.dot(bptt14,bp14)+np.dot(bptt15,bp15)+np.dot(bptt16,bp16)+bp1[0]))
    bphigh=np.ceil(np.absolute(np.dot(bptt1,bptthigh)+np.dot(bptt11,bp21)+np.dot(bptt12,bp22)+np.dot(bptt13,bp23)+np.dot(bptt14,bp24)+np.dot(bptt15,bp25)+np.dot(bptt16,bp26)+bp2[0]))


    return bplow,bphigh
