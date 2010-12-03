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
config.read("../../etc/bgp-ranking.conf")
root_dir =  config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
from ranking.compute import *

import redis

routing_db = redis.Redis(db=config.get('redis','routing_redis'))

import syslog
syslog.openlog('Compute_Ranking_Process', syslog.LOG_PID, syslog.LOG_USER)

i = 0 

syslog.syslog(syslog.LOG_INFO, '{number} rank to compute'.format(routing_db.scard(config.get('redis','to_rank'))))
r = Ranking()
while history_db.exists(config.get('redis','to_rank')):
    key = history_db.spop(config.get('redis','to_rank'))
    r.rank_using_key(key)
    i +=1 
    if i >= 1000:
        syslog.syslog(syslog.LOG_INFO, '{number} rank to compute'.format(routing_db.scard(config.get('redis','to_rank'))))
        i = 0
