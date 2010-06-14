#!/usr/bin/python

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('global','root')
sys.path.append(os.path.join(root_dir,config.get('global','lib')))
sleep_timer = int(config.get('global','sleep_timer_short'))

import syslog
syslog.openlog('BGP_Ranking_Sort_Whois_Entries', syslog.LOG_PID, syslog.LOG_USER)

import redis
from whois_client.whois_fetcher import get_server_by_query
import time

"""
A sorting processes which sort the queries by dest whois server 
"""

temp_db = redis.Redis(db=int(config.get('redis','temp_reris_db')))
key = config.get('redis','key_temp_whois')
while 1:
    syslog.syslog(syslog.LOG_INFO, 'blocs to whois: ' + str(temp_db.llen(key)))
    bloc = temp_db.lpop(key)
    if not bloc:
        time.sleep(sleep_timer)
        continue
    server = get_server_by_query(bloc)
    syslog.syslog(syslog.LOG_DEBUG, bloc + ' goto ' + server.whois )
    if not server:
        syslog.syslog(syslog.LOG_ERR, "error, no server found for this block : " + bloc)
        temp_db.rpush(key, block)
        continue
    temp_db.lpush(server.whois,  bloc)
