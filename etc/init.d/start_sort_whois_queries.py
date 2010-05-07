#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

"""
Start/stop a script which sort the queries between connectors
"""

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../bgp-ranking.conf")
root_dir = config.get('global','root')
sys.path.append(os.path.join(root_dir,config.get('global','lib')))
services_dir = os.path.join(root_dir,config.get('global','services'))


from helpers.initscript import *
import signal

def usage():
    print "start_sorting.py (start|stop|forcestop)"
    exit (1)

if len(sys.argv) < 2:
    usage()
service = os.path.join(services_dir, "sort_whois_queries")

if sys.argv[1] == "start":

    print "Starting sorting..."
    print service+" to start..."
    proc = service_start(servicename = service)
    writepid(processname = service, proc = proc)
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
