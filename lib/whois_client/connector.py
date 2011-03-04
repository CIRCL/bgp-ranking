#!/usr/bin/python
# -*- coding: utf-8 -*-
import redis
from whois_fetcher_redis import *
import errno


import time
import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config_file = "/path/to/bgp-ranking.conf"
config.read(config_file)
root_dir = config.get('directories','root')
# In case there is nothing to fetch, the process will sleep 5 seconds 
process_sleep = int(config.get('sleep_timers','short'))

# Temporary redis database, used to push ris and whois requests
temp_reris_db = int(config.get('redis','temp'))
# Cache redis database, used to set ris responses
ris_cache_reris_db = int(config.get('redis','cache_ris'))
# Cache redis database, used to set whois responses
whois_cache_reris_db = int(config.get('redis','cache_whois'))

import syslog
syslog.openlog('BGP_Ranking_Connectors', syslog.LOG_PID, syslog.LOG_USER)

# Set the ttl of the cached entries to 1 day 
cache_ttl = int(config.get('redis','cache_entries'))

desactivated_servers = config.get('whois_servers','desactivate').split()
local_whois = config.get('whois_servers','local').split()
non_routed = config.get('whois_servers', 'non_routed').split()

class Connector(object):
    """
    Make queries to a specific Whois server
    """
    keepalive = False
    support_keepalive = config.get('whois_servers', 'support_keepalive').split()
    support_keepalive += local_whois
    
    def __init__(self, server):
        """
        Initialize the two connectors to the redis server, set variables depending on the server
        Initialize a whois fetcher on this server
        """
        self.temp_db = redis.Redis(port = int(config.get('redis','port_cache')) , db=temp_reris_db)
        self.server = server
        if self.server == 'riswhois.ripe.net':
            self.cache_db = redis.Redis(port = int(config.get('redis','port_cache')), db=ris_cache_reris_db)
            self.key = config.get('redis','key_temp_ris')
        else:
            self.key = self.server
            self.cache_db = redis.Redis(port = int(config.get('redis','port_cache')), db=whois_cache_reris_db)
        if self.server in self.support_keepalive:
            self.keepalive = True
        if self.server in local_whois:
            self.fetcher = WhoisFetcher(config.get('whois_server', 'hostname'))
        else:
            self.fetcher = WhoisFetcher(self.server)
        self.connected = False
    
    def __connect(self):
        """
        Connect the fetcher
        """
        self.fetcher.connect()   
        self.connected = True

    def __disconnect(self):
        """
        Disconnect the fetcher
        """
        self.fetcher.disconnect()
        self.connected = False
    
    def launch(self):
        """
        Fetch all the whois entry to the server of this connector 
        """
        while 1:
            try:
#                syslog.syslog(syslog.LOG_DEBUG, str(self.temp_db.scard(self.key)) + ' to process on ' + self.server)
                entry = self.temp_db.spop(self.key)
                if not entry:
                    self.__disconnect()
#                    syslog.syslog(syslog.LOG_DEBUG, "Disconnected of " + self.server)
                    time.sleep(process_sleep)
                elif self.server in desactivated_servers:
                    whois = config.get('whois_servers','desactivate_message')
                    self.cache_db.setex(entry, self.server + '\n' + unicode(whois,  errors="replace"), cache_ttl)
                elif self.server in non_routed:
                    whois = config.get('whois_servers','non_routed_message')
                    self.cache_db.setex(entry, self.server + '\n' + unicode(whois,  errors="replace"), cache_ttl)
                elif self.cache_db.get(entry) is None:
                    if not self.connected:
                        self.__connect()
#                    syslog.syslog(syslog.LOG_DEBUG, self.server + ", query : " + str(entry))
                    whois = self.fetcher.fetch_whois(entry, self.keepalive)
                    if whois != '':
                        self.cache_db.setex(entry, self.server + '\n' + unicode(whois,  errors="replace"), cache_ttl)
                    if not self.keepalive:
                        self.__disconnect()
            except IOError as text:
                syslog.syslog(syslog.LOG_ERR, "IOError on " + self.server + ': ' + str(text))
                time.sleep(process_sleep)
                self.__disconnect()
