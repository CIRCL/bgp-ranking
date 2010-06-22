#!/usr/bin/python
import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('global','root')
sleep_timer = int(config.get('global','sleep_timer'))
sys.path.append(os.path.join(root_dir,config.get('global','lib')))
bgpdump = config.get('ranking','bgpdump')

import syslog
syslog.openlog('Push_BGP_Routing', syslog.LOG_PID, syslog.LOG_USER)

import time
import redis
    
"""
Push the BGP Updates
"""

def usage():
    print "push_update_routing.py filename"
    exit (1)

key = config.get('redis','key_temp_routing')
temp_db = redis.Redis(db=config.get('redis','temp_reris_db'))

filename = sys.argv[1]


from subprocess import Popen, PIPE, STDOUT

while 1:
    if not os.path.exists(filename):
        time.sleep(sleep_timer)
        continue
    p = Popen([bgpdump, filename], stdout=PIPE)
    entry = ''
    while True:
        line = p.stdout.readline()
        if not line:
            break
        if line == '\n':
            temp_db.rpush(key, entry)
            entry = ''
        else :
            entry += line
    syslog.syslog(syslog.LOG_INFO, 'Done')
    os.unlink(filename)
#    break
