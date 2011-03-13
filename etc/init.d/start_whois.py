#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

"""
Start the services looking for entries without Whois information in the database.
"""

import os 
import sys
import ConfigParser

import signal
from helpers.initscript import *
import syslog


def usage():
    print "start_get_whois_queries.py (start|stop)"
    exit (1)

if __name__ == '__main__':

    config = ConfigParser.RawConfigParser()
    config_file = "/path/to/bgp-ranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
    services_dir = os.path.join(root_dir,config.get('directories','services'))
    raw_data = os.path.join(root_dir,config.get('directories','raw_data'))

    service = os.path.join(services_dir, "whois")

    if int(config.get('whois_servers','desactivate_whois')) :
        print "Impossible to start the whois fetching: it has been desactivated in the config file"
        exit (1)

    if len(sys.argv) < 2:
        usage()

    if sys.argv[1] == "start":
        print('Start getting whois entries ')
        syslog.syslog(syslog.LOG_INFO, 'Start getting whois entries ')
        service_start_once(servicename = service, param = '',  processname = service)
    elif sys.argv[1] == "stop":
        print('Stop getting whois entries ')
        syslog.syslog(syslog.LOG_INFO, 'Stop getting whois entries ')
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
            print('Not getting whois entries')
            syslog.syslog(syslog.LOG_INFO, 'Not getting whois entries')
    else:
        usage()
