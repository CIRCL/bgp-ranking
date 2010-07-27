#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
services_dir = os.path.join(root_dir,config.get('directories','services'))
sleep_timer = int(config.get('sleep_timers','short'))

import syslog
syslog.openlog('BGP_Ranking_Get_RIS_Entries', syslog.LOG_PID, syslog.LOG_USER)

from helpers.initscript import *
from db_models.ranking import *
import time

"""
Start the getting processes on an interval of entry to process: 
use *a way* less memory and is multithreaded 
"""

service = os.path.join(services_dir, "get_range_ris_entries")
pids = []

ip_counter = init_counter(IPsDescriptions.query.filter(IPsDescriptions.asn==None).count())
while 1: 
    syslog.syslog(syslog.LOG_INFO, "Start getting RIS entries...")
    limit_first = 0
    limit_last = ip_counter['interval']
    while ip_counter['total_ips'] > 0:
        syslog.syslog(syslog.LOG_INFO, 'Actually: ' + str(len(pids)) + ' subprocess(es) are running and getting the ris whois entries.')
        while len(pids) < ip_counter['processes'] :
            if limit_first > ip_counter['total_ips']:
                limit_first = 0
                limit_last = ip_counter['interval']
            option = str(str(limit_first) + ' ' + str(limit_last))
            syslog.syslog(syslog.LOG_INFO, 'Starting interval: '+ option + '. Total ips: ' + str(ip_counter['total_ips']))
            pids.append(service_start(servicename = service, param = option))
            limit_first = limit_last +1
            limit_last += ip_counter['interval']
        if len(pids) == ip_counter['processes']:
            time.sleep(sleep_timer)
            pids = update_running_pids(pids)
        ip_counter = init_counter(IPsDescriptions.query.filter(IPsDescriptions.asn==None).count())
    time.sleep(sleep_timer)
