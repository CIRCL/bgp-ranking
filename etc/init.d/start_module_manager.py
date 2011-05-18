#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

"""
Start the module manager
"""
import os
import sys
import ConfigParser

import signal
import syslog

def usage():
    print "start_module_manager.py (start|stop)"
    exit (1)


if __name__ == '__main__':

    config = ConfigParser.RawConfigParser()
    config_file = "/path/to/bgp-ranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
    from helpers.initscript import *
    services_dir = os.path.join(root_dir,config.get('directories','services'))

    syslog.openlog('BGP_Ranking_ModuleManager', syslog.LOG_PID, syslog.LOG_LOCAL5)

    if len(sys.argv) < 2:
        usage()
    service = os.path.join(services_dir, "module_manager")

    if sys.argv[1] == "start":
        print("Starting ModuleManager...")
        syslog.syslog(syslog.LOG_INFO, "Starting ModuleManager...")
        print(service+" to start...")
        syslog.syslog(syslog.LOG_INFO, service+" to start...")
        proc = service_start_once(servicename = service, processname = service)

    elif sys.argv[1] == "stop":
        print("Stopping ModuleManager...")
        syslog.syslog(syslog.LOG_INFO, "Stopping ModuleManager...")
        pid = pidof(processname=service)
        if pid:
            pid = pid[0]
            try:
                os.kill(int(pid), signal.SIGHUP)
            except OSError, e:
                print(service+  " unsuccessfully stopped")
                syslog.syslog(syslog.LOG_ERR, service+  " unsuccessfully stopped")
            rmpid(processname=service)
        else:
            print('No running ModuleManager process')
            syslog.syslog(syslog.LOG_INFO, 'No running ModuleManager process')
    else:
        usage()

