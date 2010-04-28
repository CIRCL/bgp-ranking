#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl
#!/usr/bin/python

import sys
import os
import signal
from whois.whois_fetcher import get_all_servers
from initscript_helper import *

def usage():
    print "start_fetching.py (start|stop|forcestop)"
    exit (1)

if len(sys.argv) < 2:
    usage()

service = "whois_fetching"
whois_service_options = get_all_servers()

if sys.argv[1] == "start":

    print "Starting fetching..."
    for option in whois_service_options:
        print option+" to start..."
        pid = service_start(servicename = service, param = option)
        writepid(processname = option, pid = pid)
        print pidof(processname=option)

elif sys.argv[1] == "stop":

    print "Stopping sorting..."
    for option in whois_service_options:
        pids = pidof(processname=option)
        if pids:
            print option+" to be stopped..."
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGKILL)
                except OSError, e:
                    print option+  " unsuccessfully stopped"
            print option
            rmpid(processname=option)

elif sys.argv[1] == "forcestop":
    
    print "(forced) Stopping sorting..."
    nppidof()

else:
    usage()
