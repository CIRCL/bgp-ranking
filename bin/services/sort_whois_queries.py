#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

    :file:`bin/services/sort_whois_queries.py` - Sort the whois entries
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This service sort the queries by Whois server.
    It uses the list of assignations provided by the Debian whois client. 
    NOTE: This list has to be pushed into redis first.
    FIXME:This function has never been tested!
"""
import os 
import sys
import ConfigParser
import syslog

import redis

import time


if __name__ == '__main__':
    
    config = ConfigParser.RawConfigParser()
    config_file = "/path/to/bgp-ranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
    from whois_client.whois_fetcher_redis import get_server_by_query
    sleep_timer = int(config.get('sleep_timers','short'))

    syslog.openlog('BGP_Ranking_Sort_Whois_Entries', syslog.LOG_PID, syslog.LOG_LOCAL5)

    temp_db = redis.Redis(port = int(config.get('redis','port_cache')), db=int(config.get('redis','temp_reris')))
    key = config.get('redis','key_temp_whois')
    r = redis.Redis(db=config.get('redis','whois_assignations'))
    while 1:
    #    syslog.syslog(syslog.LOG_DEBUG, 'blocs to whois: ' + str(temp_db.llen(key)))
        block = temp_db.spop(key)
        if not block:
            time.sleep(sleep_timer)
            continue
        server = get_server_by_query(block, r)
        temp_db.sadd(server,  block)
