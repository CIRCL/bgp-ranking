#!/usr/bin/python

"""
Push the Whois entries in redis
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
syslog.openlog('BGP_Ranking_Whois_Insert', syslog.LOG_PID, syslog.LOG_USER)
from insert_Whois import InsertWhois
import time

def usage():
    print "whois.py"
    exit (1)

insertor = InsertWhois()

while 1:
    if insertor.get_whois():
        syslog.syslog(syslog.LOG_INFO, 'New Whois entries inserted in Redis.')
    time.sleep(sleep_timer)
