#!/usr/bin/python

"""
This service sort the queries by Whois server.
It uses the list of assignations provided by the Debian whois client. 
NOTE: This list has to be pushed into redis first. 
"""

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
sleep_timer = int(config.get('sleep_timers','short'))

import syslog
syslog.openlog('BGP_Ranking_Sort_Whois_Entries', syslog.LOG_PID, syslog.LOG_USER)

import redis
from whois_client.whois_fetcher_redis import get_server_by_query
import time

temp_db = redis.Redis(db=int(config.get('redis','temp_reris')))
key = config.get('redis','key_temp_whois')
r = redis.Redis(db=config.get('redis','whois_assignations'))
while 1:
#    syslog.syslog(syslog.LOG_DEBUG, 'blocs to whois: ' + str(temp_db.llen(key)))
    block = temp_db.spop(key)
    if not block:
        time.sleep(sleep_timer)
        continue
    server = get_server_by_query(block, r)
#    syslog.syslog(syslog.LOG_DEBUG, block + ' goto ' + server.whois )
    if not server:
        # FIXME: ugly. Is it used? or was it only for MySQL which did sth bad?
        syslog.syslog(syslog.LOG_ERR, "error, no server found for this block : " + block)
        temp_db.sadd(key, block)
        continue
    temp_db.sadd(server,  block)
