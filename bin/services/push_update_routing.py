#!/usr/bin/python
import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('global','root')
sleep_timer = int(config.get('global','sleep_timer'))
sys.path.append(os.path.join(root_dir,config.get('global','lib')))

import syslog
syslog.openlog('Push_BGP_Routing', syslog.LOG_PID, syslog.LOG_USER)

import time
import redis
    
"""
Push the BGP Updates from stdin
"""

def usage():
    print "push_update_routing.py"
    exit (1)

key = config.get('redis','key_temp_routing')
temp_db = redis.Redis(db=config.get('redis','temp_reris_db'))

import sys
entry = ''
for line in sys.stdin:
    if line == '\n':
        temp_db.rpush(key, entry)
        entry = ''
#        print(temp_db.llen(key))
    else :
        entry += line
