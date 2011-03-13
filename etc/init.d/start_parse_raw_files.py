#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

"""
Start a processes parsing the raw datasets for all the modules listed in 'options'
"""

import os 
import sys
import ConfigParser

import signal
import syslog



def usage():
    print("start_parse_raw_files.py (start|stop)")
    exit (1)
    

if __name__ == '__main__':
    config = ConfigParser.RawConfigParser()
    config_file = "/path/to/bgp-ranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
    from helpers.initscript import *
    services_dir = os.path.join(root_dir,config.get('directories','services'))

    if len(sys.argv) < 2:
        usage()
    service = os.path.join(services_dir, "parse_raw_files")

    items = config.items('modules_to_parse')
    options = []
    for item in items:
        options.append(item[0])

    if sys.argv[1] == "start":
        for option in options:
            print('Start parsing of ' + option)
            syslog.syslog(syslog.LOG_INFO, 'Start parsing of ' + option)
            proc = service_start_once(servicename = service, param = option, processname = service + option)
    elif sys.argv[1] == "stop":
        for option in options:
            print('Stop parsing of ' + option)
            syslog.syslog(syslog.LOG_INFO, 'Stop parsing of ' + option)
            pid = pidof(processname=service + option)
            if pid:
                pid = pid[0]
                try:
                    os.kill(int(pid), signal.SIGKILL)
                except OSError, e:
                    print(option + " unsuccessfully stopped")
                    syslog.syslog(syslog.LOG_ERR, option + " unsuccessfully stopped")
                rmpid(processname=service + option)
            else:
                print('No running parsing processes')
                syslog.syslog(syslog.LOG_INFO, 'No running parsing processes')
    else:
        usage()
