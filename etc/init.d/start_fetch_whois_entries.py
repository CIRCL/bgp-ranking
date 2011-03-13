#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

"""
Start the services fetching the (RIS) Whois information from the whois servers.
"""
import os 
import sys
import ConfigParser

import signal
import syslog

def usage():
    print "start_whois_fetching.py (start|stop)"
    exit (1)

if __name__ == '__main__':
    config = ConfigParser.RawConfigParser()
    config_file = "/path/to/bgp-ranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
    
    from whois_client.whois_fetcher_redis import get_all_servers_urls
    from helpers.initscript import *
    services_dir = os.path.join(root_dir,config.get('directories','services'))

    if len(sys.argv) < 2:
        usage()

    service = os.path.join(services_dir, "fetch_whois_entries")
    whois_service_options = get_all_servers_urls()
    syslog.syslog(syslog.LOG_DEBUG, "Servers in the database: " + str(whois_service_options))

    if sys.argv[1] == "start":

        syslog.syslog(syslog.LOG_INFO, "Starting fetching...")
        for option in whois_service_options:
            print(option + " to start...")
            syslog.syslog(syslog.LOG_INFO, option + " to start...")
            service_start_multiple(servicename = service, param = option, number = int(config.get('processes','whois_fetch')))

    elif sys.argv[1] == "stop":
        print("Stopping sorting...")
        syslog.syslog(syslog.LOG_INFO, "Stopping sorting...")
        pids = pidof(processname=service)
        if pids:
            print(service + " to be stopped...")
            syslog.syslog(syslog.LOG_INFO, service + " to be stopped...")
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGKILL)
                except OSError, e:
                    print(service +  " unsuccessfully stopped")
                    syslog.syslog(syslog.LOG_ERR, service +  " unsuccessfully stopped")
            rmpid(processname=service)
    else:
        usage()
