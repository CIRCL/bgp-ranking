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

service = os.path.join(services_dir, "get_ris_entries")

def usage():
    print "start_sort_whois_queries.py (start|stop)"
    exit (1)

if len(sys.argv) < 2:
    usage()

if sys.argv[1] == "start":
    print('Start getting ris entries ')
    syslog.syslog(syslog.LOG_INFO, 'Start getting ris entries ')
    service_start_once(servicename = service, param = '',  processname = service)
elif sys.argv[1] == "stop":
    print('Stop getting ris entries ')
    syslog.syslog(syslog.LOG_INFO, 'Stop getting ris entries ')
    pid = pidof(processname=service)
    if pid:
        pid = pid[0]
        try:
            os.kill(int(pid), signal.SIGKILL)
        except OSError, e:
            print(service +  " unsuccessfully stopped")
            syslog.syslog(syslog.LOG_ERR, service +  " unsuccessfully stopped")
        rmpid(processname=service )
    else:
        print('Not getting ris entries')
        syslog.syslog(syslog.LOG_INFO, 'Not getting ris entries')
else:
    usage()
