#!/usr/bin/python

"""
This script has two parts: 
1. pushing the routing information in a database
2. computing the ranking using the routing information 

This way, we ensure of the integrity of the routing information.
FIXME: rename the script

1. To push the routing information we have first to generate a plain text file from the 
binary dump. The second part use the splitting module to make a certain number of files 
(defined in the configuration file). When it is finished, the process start a process on 
each files to push the information into redis. And wait that each process is finished. 

2. It manages a pool of processes computing the ranking.
Using the number of processes defined in the config file, the interval assigned
to each process is computed. 
"""

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('directories','root')
sleep_timer = int(config.get('ranking','bview_check'))
sleep_timer_short = int(config.get('sleep_timers','short'))
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
services_dir = os.path.join(root_dir,config.get('directories','services'))
bgpdump = os.path.join(root_dir,config.get('routing','bgpdump'))

import syslog
syslog.openlog('Push_n_Rank', syslog.LOG_PID, syslog.LOG_USER)
import time

from db_models.ranking import *
from helpers.initscript import *

def usage():
    print "push_update_routing.py filename"
    exit (1)

import redis
routing_db = redis.Redis(db=config.get('redis','routing_redis'))
global_db = redis.Redis(db=config.get('redis','global'))
history_db = redis.Redis(db=config.get('redis','history'))

import datetime

filename = sys.argv[1]
dir = os.path.dirname(filename)

from subprocess import Popen, PIPE

from helpers.initscript import *
from helpers.files_splitter import *

def intervals_ranking(nb_of_asns, interval):
    """
    Compute the size of each intervals based on the number of ASNs found in the database
    and the number of processes defined in the configuration file
    """
    first = 0 
    intervals = []
    while first < nb_of_asns:
        intervals.append(str(first) + ' ' + str(first + interval))
        first += interval + 1
    return intervals

pushing_process_service = os.path.join(services_dir, "pushing_process")
ranking_process_service = os.path.join(services_dir, "ranking_process")

def run_splitted_processing(max_simultaneous_processes, process_name, process_args):
    pids = []
    while len(process_args) > 0:
        while len(process_args) > 0 and len(pids) < max_simultaneous_processes:
            arg = process_args.pop()
            pids.append(service_start(servicename = process_name, param = arg))
        while len(pids) == max_simultaneous_processes:
            time.sleep(sleep_timer_short)
            pids = update_running_pids(pids)
    while len(pids) > 0:
        # Wait until all the processes are finished
        time.sleep(sleep_timer_short)
        pids = update_running_pids(pids)

while 1:
    if not os.path.exists(filename) or history_db.exists(config.get('redis','to_rank')):
        # wait for a new file
        time.sleep(sleep_timer)
        continue
    syslog.syslog(syslog.LOG_INFO, 'Start converting binary bview file in plain text...')
    # create the plain text dump from the binary dump 
    output = open(dir + '/bview', 'wr')
    p_bgp = Popen([bgpdump , filename], stdout=PIPE)
    for line in p_bgp.stdout:
        output.write(line)
    output.close()
    syslog.syslog(syslog.LOG_INFO, 'Convertion finished, start splitting...')
    # Split the plain text file 
    fs = FilesSplitter(output.name, int(config.get('routing','number_of_splits')))
    splitted_files = fs.fplit()
    syslog.syslog(syslog.LOG_INFO, 'Splitting finished.')
    # Flush the old database and launch the population of the new database
    routing_db.flushdb()
    syslog.syslog(syslog.LOG_INFO, 'Start pushing all routes...')
    run_splitted_processing(int(config.get('processes','routing_push')), pushing_process_service, splitted_files)
    syslog.syslog(syslog.LOG_INFO, 'Pushing all routes done')
    # Remove the binary and the plain text files
    os.unlink(output.name)
    os.unlink(filename)
    
    
    sources = global_db.smembers('{date}{sep}{key}'.format(date.isoformat(), self.separator, config.get('redis','index_sources')))

    for source in sources:
        asns = global_db.smembers('{date}{sep}{source}'.format(date.isoformat(), self.separator, source))
        for asn in asns:
            history_db.sadd(config.get('redis','to_rank'), \
                            '{asn}{sep}{date}{sep}{source}'.format(sep = self.separator, asn = asn, date = date.isoformat(), source = source))
    
    service_start_multiple(ranking_process_service, int(config.get('processes','ranking'))
    
    while history_db.exists(config.get('redis','to_rank')):
        # wait for a new file
        time.sleep(sleep_timer_short)
    rmpid(ranking_process_service)
    routing_db.flushdb()