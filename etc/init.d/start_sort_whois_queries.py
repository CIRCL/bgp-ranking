#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

"""
Start processes sorting the queries between whois servers
"""

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config_file = "/mnt/data/gits/bgp-ranking/etc/bgp-ranking.conf"
config.read(config_file)
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
services_dir = os.path.join(root_dir,config.get('directories','services'))

from helpers.initscript import *
import signal

def usage():
    print "start_sort_whois_queries.py (start|stop)"
    exit (1)

if int(config.get('whois_servers','desactivate_whois')) :
    print "Impossible to start the whois sorting: it has been desactivated in the config file"
    exit (1)

if len(sys.argv) < 2:
    usage()
service = os.path.join(services_dir, "sort_whois_queries")

if sys.argv[1] == "start":
    print("Starting sorting...")
    syslog.syslog(syslog.LOG_INFO, "Starting sorting...")
    print(service+" to start...")
    syslog.syslog(syslog.LOG_INFO, service+" to start...")
    service_start_multiple(servicename = service, number = int(config.get('whois_servers','sorting_processes')))

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
