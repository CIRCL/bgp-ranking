#!/usr/bin/python

"""
Push the RIS entries in redis
"""

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config_file = "/home/rvinot/bgp-ranking/etc/bgp-ranking.conf"
config.read(config_file)
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
sleep_timer = int(config.get('sleep_timers','short'))

import syslog
syslog.openlog('BGP_Ranking_RIS_Whois_Insert', syslog.LOG_PID, syslog.LOG_USER)
from insert_ris import InsertRIS
import time

def usage():
    print "ris.py"
    exit (1)

insertor = InsertRIS()

while 1:
    if insertor.get_ris():
        syslog.syslog(syslog.LOG_INFO, 'New RIS entries inserted in Redis.')
    time.sleep(sleep_timer)
