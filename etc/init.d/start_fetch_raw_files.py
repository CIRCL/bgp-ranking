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
raw_data = os.path.join(root_dir,config.get('global','raw_data'))

import signal

from helpers.initscript import *

"""
Launch the raw fetching processes 
"""

service = os.path.join(services_dir, "fetch_raw_files")

options = \
        {'DshieldTopIPs'        :   os.path.join(raw_data, 'dshield/topips/')  + ' http://www.dshield.org/feeds/topips.txt', 
        'DshieldDaily'          :   os.path.join(raw_data, 'dshield/daily/')   + ' http://www.dshield.org/feeds/daily_sources', 
        'ZeustrackerIpBlockList':   os.path.join(raw_data, 'zeus/ipblocklist/')+ ' http://www.abuse.ch/zeustracker/blocklist.php?download=ipblocklist'}

def usage():
    print "start_sort_whois_queries.py (start|stop)"
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
