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

import signal

from helpers.initscript import *

"""
Launch the fetching of the whois databases
"""

service = os.path.join(services_dir, "fetch_db_dumps")

options = \
        {'RIPE'     :   'ftp://ftp.ripe.net/ripe/dbase/RIPE.CURRENTSERIAL ftp://ftp.ripe.net/ripe/dbase/ripe.db.gz'}

def usage():
    print "start_fetch_db_dumps.py (start|stop)"
    exit (1)

if len(sys.argv) < 2:
    usage()

if sys.argv[1] == "start":
    for name, option in options.iteritems():
        print('Start fetching of ' + name)
        proc = service_start_once(servicename = service, param = option,  processname = service + name)
elif sys.argv[1] == "stop":
    for name in options.keys():
        print('Stop fetching of ' + name)
        pid = pidof(processname=service + name)
        if pid:
            pid = pid[0]
            try:
                os.kill(int(pid), signal.SIGKILL)
            except OSError, e:
                print name +  " unsuccessfully stopped"
            rmpid(processname=service + name)
        else:
            print('No running fetching processes')
else:
    usage()
