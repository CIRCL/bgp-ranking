#!/usr/bin/python

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('global','root')
sys.path.append(os.path.join(root_dir,config.get('global','lib')))
sleep_timer = int(config.get('global','sleep_timer_short'))

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=os.path.join(root_dir,config.get('global','log_sort_whois')))

import redis
from whois_client.whois_fetcher import get_server_by_query
import time

"""
A sorting processes which sort the queries by dest whois server 
"""

temp_db = redis.Redis(db=int(config.get('redis','temp_reris_db')))
key = config.get('redis','key_temp_whois')
while 1:
    print('blocs to whois: ' + str(temp_db.llen(key)))
    logging.info('blocs to whois: ' + str(temp_db.llen(key)))
    bloc = temp_db.lpop(key)
    if not bloc:
        time.sleep(sleep_timer)
        continue
    server = get_server_by_query(bloc)
    if not server:
        print("error, no server found for this block : " + bloc)
        logging.info("error, no server found for this block : " + bloc)
        temp_db.rpush(key, block)
        continue
    temp_db.lpush(server.whois,  bloc)
