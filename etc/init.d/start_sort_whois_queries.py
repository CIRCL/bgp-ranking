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
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
services_dir = os.path.join(root_dir,config.get('directories','services'))

from helpers.initscript import *
import signal

def usage():
    print "start_sort_whois_queries.py (start|stop)"
    exit (1)

if len(sys.argv) < 2:
    usage()
service = os.path.join(services_dir, "sort_whois_queries")

if sys.argv[1] == "start":
    print("Starting sorting...")
    syslog.syslog(syslog.LOG_INFO, "Starting sorting...")
    print(service+" to start...")
    syslog.syslog(syslog.LOG_INFO, service+" to start...")
    service_start_multiple(servicename = service, param = option,  number = int(config.get('whois_servers','processes_by_servers')))

elif sys.argv[1] == "stop":
    print("Stopping sorting...")
    syslog.syslog(syslog.LOG_INFO, "Stopping sorting...")
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
