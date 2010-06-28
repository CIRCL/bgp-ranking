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

import signal

from helpers.initscript import *

"""
Launch the raw fetching processes 
"""

service = os.path.join(services_dir, "update_routing_db")
option = 'RIPE'

def usage():
    print "start_update_routing_db.py (start|stop)"
    exit (1)

if len(sys.argv) < 2:
    usage()

if sys.argv[1] == "start":
    print("Starting update routing...")
    syslog.syslog(syslog.LOG_INFO, "Starting update routing...")
    print(service+" to start...")
    syslog.syslog(syslog.LOG_INFO, service+" to start...")
    service_start_multiple(servicename = service, param = option,  number = int(config.get('ranking','routing_db_processes')))

elif sys.argv[1] == "stop":
    print("Stopping update routing...")
    syslog.syslog(syslog.LOG_INFO, "Stopping update routing...")
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
