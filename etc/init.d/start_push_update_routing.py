#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

"""
Start the process pushing the update of the routing information. 
NOTE: it will also compute the ranking 

FIXME: rename the script 
"""

def usage():
    print "start_push_update_routing.py (start|stop)"
    exit (1)

if __name__ == '__main__':

    import os 
    import sys
    import ConfigParser
    config = ConfigParser.RawConfigParser()
    config_file = "/path/to/bgp-ranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
    services_dir = os.path.join(root_dir,config.get('directories','services'))
    raw_data = os.path.join(root_dir,config.get('directories','raw_data'))

    import signal

    from helpers.initscript import *
    from helpers.files_splitter import *

    service = os.path.join(services_dir, "push_update_routing")
    option = os.path.join(raw_data, config.get('routing','bviewfile'))

    if len(sys.argv) < 2:
        usage()

    if sys.argv[1] == "start":
        print("Start pushing routes...")
        syslog.syslog(syslog.LOG_INFO, "Start pushing routes...")
        print(service+" to start...")
        syslog.syslog(syslog.LOG_INFO, service+" to start...")
        proc = service_start_once(servicename = service, param = option,  processname = service)

    elif sys.argv[1] == "stop":
        print("Stop pushing routes...")
        syslog.syslog(syslog.LOG_INFO, "Stop pushing routes...")
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
