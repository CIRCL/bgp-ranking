#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../bgp-ranking.conf")
root_dir = config.get('global','root')
sys.path.append(os.path.join(root_dir,config.get('global','lib')))
services_dir = os.path.join(root_dir,config.get('global','services'))
raw_data = os.path.join(root_dir,config.get('global','raw_data'))

import signal

from helpers.initscript import *

"""
Launch the raw fetching processes 
"""

service = os.path.join(services_dir, "push_update_routing")


def usage():
    print "start_push_update_routing.py (start|stop)"
    exit (1)

if len(sys.argv) < 2:
    usage()

if sys.argv[1] == "start":
    print("Start pushing routes...")
    syslog.syslog(syslog.LOG_INFO, "Start pushing routes...")
    print(service+" to start...")
    syslog.syslog(syslog.LOG_INFO, service+" to start...")
    proc = service_start(servicename = service)
    writepid(processname = service, proc = proc)

elif sys.argv[1] == "stop":
    print("Stop pushing routes...")
    syslog.syslog(syslog.LOG_INFO, "Stop pushing routes...")
    pids = pidof(processname=service)
    if pids:
        print(service+" to be stopped...")
        syslog.syslog(syslog.LOG_INFO, service+" to be stopped...")
        for pid in pids:
            try:
                os.kill(int(pid), signal.SIGKILL)
            except OSError, e:
                print(service+  " unsuccessfully stopped")
                syslog.syslog(syslog.LOG_ERR, service+  " unsuccessfully stopped")
        rmpid(processname=service)

else:
    usage()
