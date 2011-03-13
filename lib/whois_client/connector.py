#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Connector
    ~~~~~~~~~
    
    Initialize a connection to a whois server
"""
import redis
from whois_fetcher_redis import *
import errno


import time
import os 
import sys
import ConfigParser
import syslog

class Connector(object):
    """
        Query a specific Whois server
    """
    
    def __init__(self, server):
        """
            Set variables depending on the server, initialize a whois fetcher on this server
        """
        
        self.config = ConfigParser.RawConfigParser()
        config_file = "/path/to/bgp-ranking.conf"
        self.config.read(config_file)
        # In case there is nothing to fetch, the process will sleep 5 seconds 
        self.process_sleep = int(self.config.get('sleep_timers','short'))
        
        syslog.openlog('BGP_Ranking_Connectors', syslog.LOG_PID, syslog.LOG_USER)

        # Set the ttl of the cached entries to 1 day 
        self.cache_ttl = int(self.config.get('redis','cache_entries'))

        self.local_whois = self.config.get('whois_servers','local').split()
        
        
        self.keepalive = False
        self.support_keepalive = self.config.get('whois_servers', 'support_keepalive').split()
        self.support_keepalive += self.local_whois
        
        self.temp_db = redis.Redis(port = int(self.config.get('redis','port_cache')) , db=int(self.config.get('redis','temp')))
        self.server = server
        if self.server == 'riswhois.ripe.net':
            self.cache_db = redis.Redis(port = int(self.config.get('redis','port_cache')), db=int(self.config.get('redis','cache_ris')))
            self.key = self.config.get('redis','key_temp_ris')
        else:
            self.key = self.server
            self.cache_db = redis.Redis(port = int(self.config.get('redis','port_cache')), db=int(self.config.get('redis','cache_whois')))
        if self.server in self.support_keepalive:
            self.keepalive = True
        if self.server in self.local_whois:
            self.fetcher = WhoisFetcher(self.config.get('whois_server', 'hostname'))
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
                    time.sleep(self.process_sleep)
                elif self.server in self.config.get('whois_servers','desactivate').split():
                    whois = self.config.get('whois_servers','desactivate_message')
                    self.cache_db.setex(entry, self.server + '\n' + unicode(whois,  errors="replace"), self.cache_ttl)
                elif self.server in self.config.get('whois_servers', 'non_routed').split():
                    whois = self.config.get('whois_servers','non_routed_message')
                    self.cache_db.setex(entry, self.server + '\n' + unicode(whois,  errors="replace"), self.cache_ttl)
                elif self.cache_db.get(entry) is None:
                    if not self.connected:
                        self.__connect()
#                    syslog.syslog(syslog.LOG_DEBUG, self.server + ", query : " + str(entry))
                    whois = self.fetcher.fetch_whois(entry, self.keepalive)
                    if whois != '':
                        self.cache_db.setex(entry, self.server + '\n' + unicode(whois,  errors="replace"), self.cache_ttl)
                    if not self.keepalive:
                        self.__disconnect()
            except IOError as text:
                syslog.syslog(syslog.LOG_ERR, "IOError on " + self.server + ': ' + str(text))
                time.sleep(self.process_sleep)
                self.__disconnect()
