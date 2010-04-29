#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

import sys
import os
import signal
from initscript_helper import *

def usage():
    print "start_sorting.py (start|stop|forcestop)"
    exit (1)

if len(sys.argv) < 2:
    usage()

service = "whois_sorting"

if sys.argv[1] == "start":

    print "Starting sorting..."
    print service+" to start..."
    pid = service_start(servicename = service)
    writepid(processname = service, pid = pid)
    print pidof(processname=service)

elif sys.argv[1] == "stop":

    print "Stopping sorting..."
    pids = pidof(processname=service)
    if pids:
        print service+" to be stopped..."
        for pid in pids:
            try:
                os.kill(int(pid), signal.SIGKILL)
            except OSError, e:
                print service+  " unsuccessfully stopped"
        print service
        rmpid(processname=service)

elif sys.argv[1] == "forcestop":
    
    print "(forced) Stopping sorting..."
    nppidof()

else:
    usage()
