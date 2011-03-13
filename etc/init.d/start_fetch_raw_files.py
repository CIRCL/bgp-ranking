#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

"""
Start the service fetching the raw datasets
"""
import os 
import sys
import ConfigParser

import signal

from helpers.initscript import *
import syslog

def usage():
    print "start_fetch_raw_files.py (start|stop)"
    exit (1)

if __name__ == '__main__':
    config = ConfigParser.RawConfigParser()
    config_file = "/path/to/bgp-ranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
    services_dir = os.path.join(root_dir,config.get('directories','services'))
    raw_data = os.path.join(root_dir,config.get('directories','raw_data'))

    service = os.path.join(services_dir, "fetch_raw_files")

    items = config.items('raw_fetching')

    options = {}
    for item in items:
        elts = item[1].split()
        options[elts[0]] = os.path.join(raw_data, elts[1]) + ' ' + elts[2]


    def usage():
        print "start_fetch_raw_files.py (start|stop)"
        exit (1)

    if len(sys.argv) < 2:
        usage()

    if sys.argv[1] == "start":
        for name, option in options.iteritems():
            print('Start fetching of ' + name)
            syslog.syslog(syslog.LOG_INFO, 'Start fetching of ' + name)
            proc = service_start_once(servicename = service, param = option,  processname = service + name)
    elif sys.argv[1] == "stop":
        for name in options.keys():
            print('Stop fetching of ' + name)
            syslog.syslog(syslog.LOG_INFO, 'Stop fetching of ' + name)
            pid = pidof(processname=service + name)
            if pid:
                pid = pid[0]
                try:
                    os.kill(int(pid), signal.SIGKILL)
                except OSError, e:
                    print(name +  " unsuccessfully stopped")
                    syslog.syslog(syslog.LOG_ERR, name +  " unsuccessfully stopped")
                rmpid(processname=service + name)
            else:
                print('No running fetching processes')
                syslog.syslog(syslog.LOG_INFO, 'No running fetching processes')
    else:
        usage()
