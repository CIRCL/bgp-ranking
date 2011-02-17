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
config_file = "/mnt/data/gits/bgp-ranking/etc/bgp-ranking.conf"
config.read(config_file)
root_dir = config.get('directories','root')
sleep_timer = int(config.get('ranking','bview_check'))
sleep_timer_short = int(config.get('sleep_timers','short'))
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
services_dir = os.path.join(root_dir,config.get('directories','services'))
bgpdump = os.path.join(root_dir,config.get('routing','bgpdump'))

import syslog
syslog.openlog('Push_n_Rank', syslog.LOG_PID, syslog.LOG_USER)
import time

from helpers.initscript import *

def usage():
    print "push_update_routing.py filename"
    exit (1)

import redis
routing_db = redis.Redis(db=config.get('redis','routing'))
global_db = redis.Redis(db=config.get('redis','global'))
global_db_slave = redis.Redis(port = int(config.get('redis','port_slave_1')), db=config.get('redis','global'))
history_db = redis.Redis(db=config.get('redis','history'))
history_db_slave = redis.Redis(port = int(config.get('redis','port_slave_1')), db=config.get('redis','history'))

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

def compute_yesterday_ranking():
    # if the bview file has been generated at midnight, it is better to compute the ranking of "yesterday"
    hours = sorted(config.get('routing','update_hours').split())
    first_hour = hours[0]
    raw_data = os.path.join(root_dir,config.get('directories','raw_data'))
    ts_file = os.path.join(raw_data, config.get('routing','bviewtimesamp'))
    if os.path.exists(ts_file):
        ts = open(ts_file, 'r').read()
        history_db.set(config.get('ranking','latest_ranking'), ts)
        ts = ts.split()
        if int(ts[1]) == int(first_hour):
            return True
    return False

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
    
    if compute_yesterday_ranking():
        date = (datetime.date.today() - datetime.timedelta(1)).isoformat()
    else:
        date = datetime.date.today().isoformat()
    separator = config.get('input_keys','separator')
    sources = global_db.smembers('{date}{sep}{key}'.format(date = date, sep = separator, key = config.get('input_keys','index_sources')))
    
    pipeline = history_db.pipeline()
    to_delete = []
    for source in sources:
        asns = global_db.smembers('{date}{sep}{source}{sep}{key}'.format(date = date, sep = separator, source = source, \
                                            key = config.get('input_keys','index_asns_details')))
        for asn in asns:
            global_asn = asn.split(separator)[0]
            asn_key_v4 = '{asn}{sep}{date}{sep}{source}{sep}{v4}'.format(sep = separator, asn = global_asn, \
                            date = date, source = source, v4 = config.get('input_keys','rankv4'))
            asn_key_v6 = '{asn}{sep}{date}{sep}{source}{sep}{v6}'.format(sep = separator, asn = global_asn, \
                            date = date, source = source, v6 = config.get('input_keys','rankv6'))
            to_delete.append(asn_key_v4)
            to_delete.append(asn_key_v6)

            pipeline.sadd(config.get('redis','to_rank'), '{asn}{sep}{date}{sep}{source}'.format(sep = separator, asn = asn, date = date, source = source))
    to_delete = set(to_delete)
    pipeline.delete(*to_delete)
    pipeline.execute()

    service_start_multiple(ranking_process_service, int(config.get('processes','ranking')))
    
    while history_db.scard(config.get('redis','to_rank')) > 0:
        # wait for a new file
        time.sleep(sleep_timer_short)
    rmpid(ranking_process_service)
    routing_db.flushdb()