#!/usr/bin/python
import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
raw_data = os.path.join(root_dir,config.get('directories','raw_data'))
sleep_timer = int(config.get('sleep_timers','short'))

import syslog
syslog.openlog('BGP_Ranking_Get_Whois_Entries', syslog.LOG_PID, syslog.LOG_USER)

from modules import *

import time

"""
Parse the file of a module
"""

def usage():
    print "parse_raw_files.py name"
    exit (1)

if len(sys.argv) < 2:
    usage()

while 1:
    module = eval(sys.argv[1])(raw_data)
    if module.update():
        syslog.syslog(syslog.LOG_INFO, 'Done with ' + sys.argv[1])
    else:
#        syslog.syslog(syslog.LOG_DEBUG, 'No files to parse for ' + sys.argv[1])
        pass
    time.sleep(sleep_timer)
