#!/usr/bin/python

"""
Push the entries he finds in redis in the MySQL database
"""

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config_file = "/mnt/data/gits/bgp-ranking/etc/bgp-ranking.conf"
config.read(config_file)
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
sleep_timer = int(config.get('sleep_timers','short'))

import syslog
syslog.openlog('BGP_Ranking_DB_Input', syslog.LOG_PID, syslog.LOG_USER)
from input_reader import InputReader
import time

def usage():
    print "db_input.py"
    exit (1)

reader = InputReader()
reader.connect()

while 1:
    if reader.insert():
        syslog.syslog(syslog.LOG_INFO, 'New entries inserted in Redis.')
    time.sleep(sleep_timer)

reader.disconnect()
