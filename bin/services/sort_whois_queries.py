#!/usr/bin/python

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../bgp-ranking.conf")
root_dir = config.get('global','root')
sys.path.append(os.path.join(root_dir,config.get('global','lib')))

import redis
from whois_client.whois_fetcher import get_server_by_query
import time

"""
A sorting processes which sort the queries by dest whois server 
"""


redis_keys = ['ris', 'whois']
# Temporary redis database, used to push ris and whois requests
temp_reris_db = 0
# Cache redis database, used to set ris responses
ris_cache_reris_db = 1
# Cache redis database, used to set whois responses
whois_cache_reris_db = 2
# Sleep before fetch the deferred queries

process_sleep = 5

temp_db = redis.Redis(db=temp_reris_db)
key = redis_keys[1]
while 1:
    print('blocs to whois: ' + str(temp_db.llen(key)))
    bloc = temp_db.pop(key)
    if not bloc:
        time.sleep(process_sleep)
        continue
    server = get_server_by_query(bloc)
    if not server:
        print ("error, no server found for this block : " + bloc)
        temp_db.push(key, block)
        continue
    temp_db.push(server.whois,  bloc)
