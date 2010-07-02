#!/usr/bin/python
import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('global','root')
sleep_timer = int(config.get('global','sleep_timer'))
sleep_timer_short = int(config.get('global','sleep_timer_short'))
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
dir = os.path.dirname(filename)

from subprocess import Popen, PIPE, STDOUT
from multiprocessing import Process


from helpers.initscript import *

while 1:
    if not os.path.exists(filename):
        time.sleep(sleep_timer)
        continue
    output = open(dir + '/bview', 'wr')
    p = os.system(bgpdump + ' ' + filename + '>' + dir + '/bview')
    while check_pid(p):
        time.sleep(sleep_timer_short)
        continue
    fs = FilesSplitter(output)
    output.close()
    fs.fplit()
    processes = []
    print fs.splitted_files
    for file in fs.splitted_files:
        processes.append(Process(target=splittet_file_parser, args=(file,)))
    while len(update_running_pids(processes)) > 0:
        time.sleep(sleep_timer_short)
        continue
    syslog.syslog(syslog.LOG_INFO, 'Done')
#    os.unlink(filename)
    
def splittet_file_parser(fname):
    file = open(fname)
    entry = ''
    for line in file:
        if not line:
            break
        if line == '\n':
            temp_db.rpush(key, entry)
            entry = ''
        else :
            entry += line
    syslog.syslog(syslog.LOG_INFO, 'Done')
    os.unlink(fname)
#    break
