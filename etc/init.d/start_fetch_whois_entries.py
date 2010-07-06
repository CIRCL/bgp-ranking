#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

"""
Start/stop a connector to each whois server we know. 
"""

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../bgp-ranking.conf")
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
services_dir = os.path.join(root_dir,config.get('directories','services'))

import signal
from whois_client.whois_fetcher_redis import get_all_servers_urls
from helpers.initscript import *

def usage():
    print "start_whois_fetching.py (start|stop)"
    exit (1)

if len(sys.argv) < 2:
    usage()

service = os.path.join(services_dir, "fetch_whois_entries")
whois_service_options = get_all_servers_urls()

desactivated_whois_servers = config.get('whois_servers','desactivate').split()
for server in desactivated_whois_servers:
    whois_service_options.remove(server)

if sys.argv[1] == "start":

    syslog.syslog(syslog.LOG_INFO, "Starting fetching...")
    for option in whois_service_options:
        print(option + " to start...")
        syslog.syslog(syslog.LOG_INFO, option + " to start...")
        service_start_multiple(servicename = service, param = option, number = int(config.get('whois_servers','fetching_processes')))

elif sys.argv[1] == "stop":
    print("Stopping sorting...")
    syslog.syslog(syslog.LOG_INFO, "Stopping sorting...")
    for option in whois_service_options:
        pids = pidof(processname=option)
        if pids:
            print(option + " to be stopped...")
            syslog.syslog(syslog.LOG_INFO, option + " to be stopped...")
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGKILL)
                except OSError, e:
                    print(option +  " unsuccessfully stopped")
                    syslog.syslog(syslog.LOG_ERR, option +  " unsuccessfully stopped")
            rmpid(processname=option)
else:
    usage()
