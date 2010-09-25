#!/usr/bin/python

"""
Main process getting the RIS Whois entries. 
This process manages a pool of processes working on an interval of entries in the database 
without RIS Whois information. The number of processes and the size of the intervals 
is defined in the config file. 

This method allows us to use very few memory and start as much concurrent processes as we want.

FIXME: It would be great to find a way to merge the fetching of RIS Whois and Whois entries
"""

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



service = os.path.join(services_dir, "get_range_ris_entries")
pids = []

while 1: 
    ip_counter = init_counter(IPsDescriptions.query.filter(IPsDescriptions.asn==None).count())
#    syslog.syslog(syslog.LOG_DEBUG, "Start getting RIS entries...")
    limit_first = 0
    limit_last = ip_counter['interval']
    while ip_counter['total_ips'] > 0:
        if ip_counter['total_ips'] <= ip_counter['interval']:
            # Do not start more than one process if the total of IP Addresses to use is 
            # smaller than the maximal size of an interval
            ip_counter['processes'] = 1
        syslog.syslog(syslog.LOG_INFO, 'Actually: ' + str(len(pids)) + ' subprocess(es) are running and getting the ris whois entries.')
        while len(pids) < ip_counter['processes'] :
            # Start the processes on their intervals 
            if limit_first > ip_counter['total_ips'] or ip_counter['processes'] == 1:
                limit_first = 0
                limit_last = ip_counter['interval']
            option = str(str(limit_first) + ' ' + str(limit_last))
            syslog.syslog(syslog.LOG_INFO, 'Starting interval: '+ option + '. Total RIS: ' + str(ip_counter['total_ips']))
            pids.append(service_start(servicename = service, param = option))
            limit_first = limit_last +1
            limit_last += ip_counter['interval']
        pids = update_running_pids(pids)
        if len(pids) >= ip_counter['processes']:
            # Wait until one or more processes are finished
            time.sleep(sleep_timer)
        ip_counter = init_counter(IPsDescriptions.query.filter(IPsDescriptions.asn==None).count())
    time.sleep(sleep_timer)