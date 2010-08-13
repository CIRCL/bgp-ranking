#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../bgp-ranking.conf")
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
services_dir = os.path.join(root_dir,config.get('directories','services'))

import signal

from helpers.initscript import *

"""
Launch the raw fetching processes 
"""

service = os.path.join(services_dir, "meta_ranking")


def usage():
    print "start_meta_ranking.py (start|stop)"
    exit (1)

if len(sys.argv) < 2:
    usage()

if sys.argv[1] == "start":
    print('Start Ranking')
    syslog.syslog(syslog.LOG_INFO, 'Start Ranking')
    proc = service_start_once(servicename = service, processname = service)
elif sys.argv[1] == "stop":
    print('Stop Ranking')
    syslog.syslog(syslog.LOG_INFO, 'Stop Ranking')
    pid = pidof(processname=service)
    if pid:
        pid = pid[0]
        try:
            os.kill(int(pid), signal.SIGKILL)
        except OSError, e:
            print("Ranking unsuccessfully stopped")
            syslog.syslog(syslog.LOG_ERR,"Ranking unsuccessfully stopped")
        rmpid(processname=service)
    else:
        print('No running Ranking processes')
        syslog.syslog(syslog.LOG_INFO, 'No running Ranking processes')
else:
    usage()
