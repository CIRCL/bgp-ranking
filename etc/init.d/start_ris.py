#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

"""
Start the services looking for entries without RIS Whois information in the database.
"""

import os 
import sys
import ConfigParser
import signal
import syslog

def usage():
    print "start_ris.py (start|stop)"
    exit (1)

if __name__ == '__main__':

    config = ConfigParser.RawConfigParser()
    config_file = "/path/to/bgp-ranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
    from helpers.initscript import *
    services_dir = os.path.join(root_dir,config.get('directories','services'))
    
    syslog.openlog('BGP_Ranking_RIS', syslog.LOG_PID, syslog.LOG_LOCAL5)


    if len(sys.argv) < 2:
        usage()
    service = os.path.join(services_dir, "ris")

    if sys.argv[1] == "start":
        print("Starting insertion...")
        syslog.syslog(syslog.LOG_INFO, "Starting insertion...")
        print(service+" to start...")
        syslog.syslog(syslog.LOG_INFO, service+" to start...")
        service_start_multiple(servicename = service, number = int(config.get('processes','whois_fetch')))

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
