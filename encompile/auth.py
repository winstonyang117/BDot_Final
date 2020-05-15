#!/usr/bin/python2.7

import subprocess
import sys

key = 'sensorweb987'

serial = subprocess.check_output('cat /proc/cpuinfo | grep Serial | awk \'{print($3)}\'', shell=True)[:-1]

try:
    cmp_serial = subprocess.check_output('openssl enc -d -a -aes-256-cbc -pass pass:%s -in key 2>/dev/null' % (key), shell=True).split('\n')[0]
except:
    print 'Permission denied.'
    sys.exit() 

if serial == cmp_serial:
    print "Validate successful!"
    try:
        # the entry point of our code
        import _main 
    except Exception as error:
        print 'main module missing.' + str(error)
    _main.main()
else:
    print 'Permission denied.'
