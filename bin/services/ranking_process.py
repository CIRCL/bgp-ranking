#!/usr/bin/python

"""
Service computing the ranking. 
For each ASN of the interval, compute the ranking.
"""

import os
import sys
import IPy
import ConfigParser
config = ConfigParser.RawConfigParser()
config_file = "/path/to/bgp-ranking.conf"
config.read(config_file)
root_dir =  config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
sleep_timer = int(config.get('sleep_timers','short'))

from ranking.compute import *

import redis

routing_db = redis.Redis(db=config.get('redis','routing'))

import syslog
syslog.openlog('Compute_Ranking_Process', syslog.LOG_PID, syslog.LOG_USER)

i = 0 

time.sleep(sleep_timer)
syslog.syslog(syslog.LOG_INFO, '{number} rank to compute'.format(number = history_db.scard(config.get('redis','to_rank'))))
r = Ranking()
#r.update_asn_list()
# asn|timestamp|date|source => lookup all the ASNs & drop all the ranks of today
while history_db.scard(config.get('redis','to_rank')) > 0 :
    key = history_db.spop(config.get('redis','to_rank'))
    if key is not None:
        r.rank_using_key(key)
        i +=1 
        if i >= 1000:
            #r.update_asn_list()
            syslog.syslog(syslog.LOG_INFO, '{number} rank to compute'.format(number = history_db.scard(config.get('redis','to_rank'))))
            i = 0
