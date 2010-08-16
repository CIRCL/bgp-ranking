#!/usr/bin/python
import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('directories','root')
sleep_timer = int(config.get('sleep_timers','long'))
sleep_timer_short = int(config.get('sleep_timers','short'))
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
services_dir = os.path.join(root_dir,config.get('directories','services'))
bgpdump = config.get('routing','bgpdump')
import syslog
syslog.openlog('Push_BGP_Routing', syslog.LOG_PID, syslog.LOG_USER)

import time
import redis
import subprocess


from db_models.ranking import *
from helpers.initscript import *
from whois_parser.bgp_parsers import *

"""
Push the BGP Updates
"""

def usage():
    print "push_update_routing.py filename"
    exit (1)

key = config.get('redis','key_temp_routing')
temp_db = redis.Redis(db=config.get('redis','temp_reris_db'))
routing_db = redis.Redis(db=config.get('redis','routing_redis_db'))

filename = sys.argv[1]
dir = os.path.dirname(filename)

from subprocess import Popen, PIPE
from multiprocessing import Process


from helpers.initscript import *
from helpers.files_splitter import *

def splitted_file_parser(fname):
    file = open(fname)
    entry = ''
    for line in file:
        if not line:
            break
        if line == '\n':
            parsed = BGP(entry,  'RIPE')
            if parsed.asn is not None:
                asn = parsed.asn.split()[-1]
                block = parsed.prefix
                if block is not None:
                    routing_db.sadd(asn, block)
                    routing_db.sadd(block, asn)
                entry = ''
        else :
            entry += line
    syslog.syslog(syslog.LOG_INFO, fname + ' done')
    os.unlink(fname)

def intervals_ranking(nb_of_asns):
    interval = nb_of_asns / int(config.get('ranking','processes'))
    first = 0 
    intervals = []
    while first < nb_of_asns:
        intervals.append([first, first + interval])
        first += interval + 1
    return intervals

ranking_process_service = os.path.join(services_dir, "ranking_process")

while 1:
    if not os.path.exists(filename):
        time.sleep(sleep_timer)
        continue
    output = open(dir + '/bview', 'wr')
    p_bgp = Popen([bgpdump , filename], stdout=PIPE)
    for line in p_bgp.stdout:
        output.write(line)
    output.close()
    fs = FilesSplitter(output.name, int(config.get('routing','processes_push')))
    splitted_files = fs.fplit()
    processes = []
    routing_db.flushdb()
    for file in splitted_files:
        p = Process(target=splitted_file_parser, args=(file, ))
        p.start()
        processes.append(p)
    for p in processes:
        p.join()
    syslog.syslog(syslog.LOG_INFO, 'Pushing all routes done')
    os.unlink(output.name)
    os.unlink(filename)
    
    # start computing
    syslog.syslog(syslog.LOG_INFO, 'Start compute ranking')
    nb_of_asns = ASNs.query.count()
    all_intervals = intervals_ranking(nb_of_asns)
    pids = []
    for interval in all_intervals:
        pids.append(service_start(servicename = ranking_process_service, param = str(interval[0]) + ' ' + str(interval[1])))

    while len(pids) > 0:
        pids = update_running_pids(pids)
        time.sleep(sleep_timer_short)
    syslog.syslog(syslog.LOG_INFO, 'Ranking computed')
