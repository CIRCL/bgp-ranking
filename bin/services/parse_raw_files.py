#!/usr/bin/python

"""
Launche the parsing of a particular raw file.
"""

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config_file = "/path/to/bgp-ranking.conf"
config.read(config_file)
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
raw_data = os.path.join(root_dir,config.get('directories','raw_data'))
sleep_timer = int(config.get('sleep_timers','short'))

import syslog
syslog.openlog('BGP_Ranking_Get_Whois_Entries', syslog.LOG_PID, syslog.LOG_USER)
from modules import *
import time

def usage():
    print "parse_raw_files.py name"
    exit (1)

if len(sys.argv) < 2:
    usage()

module = eval(sys.argv[1])(raw_data)
while 1:
    if module.update():
        syslog.syslog(syslog.LOG_INFO, 'Done with ' + sys.argv[1])
    else:
#        syslog.syslog(syslog.LOG_DEBUG, 'No files to parse for ' + sys.argv[1])
        pass
    time.sleep(sleep_timer)
