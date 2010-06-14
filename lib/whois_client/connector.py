#!/usr/bin/python
# -*- coding: utf-8 -*-
import redis
from whois_fetcher import *
import errno


import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('global','root')
# In case there is nothing to fetch, the process will sleep 5 seconds 
process_sleep = int(config.get('global','sleep_timer_short'))

# Temporary redis database, used to push ris and whois requests
temp_reris_db = int(config.get('redis','temp_reris_db'))
# Cache redis database, used to set ris responses
ris_cache_reris_db = int(config.get('redis','ris_cache_reris_db'))
# Cache redis database, used to set whois responses
whois_cache_reris_db = int(config.get('redis','whois_cache_reris_db'))

import syslog
syslog.openlog('BGP_Ranking_Connectors', syslog.LOG_PID, syslog.LOG_USER)

# Set the ttl of the cached entries to 1 day 
cache_ttl = int(config.get('redis','cache_entries'))

class Connector(object):
    """
    Make queries to a specific Whois server
    """
    keepalive = False
    support_keepalive = ['riswhois.ripe.net', 'whois.ripe.net']
    
    def __init__(self, server):
        """
        Initialize the two connectors to the redis server, set variables depending on the server
        Initialize a whois fetcher on this server
        """
        self.temp_db = redis.Redis(db=temp_reris_db)
        self.server = server
        if self.server == 'riswhois.ripe.net':
            self.cache_db = redis.Redis(db=ris_cache_reris_db)
            self.key = config.get('redis','key_temp_ris')
        else:
            self.key = self.server
            self.cache_db = redis.Redis(db=whois_cache_reris_db)
        if self.server in self.support_keepalive:
            self.keepalive = True
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
                syslog.syslog(syslog.LOG_INFO, str(self.temp_db.llen(self.key)) + ' to process on ' + self.server)
                entry = self.temp_db.lpop(self.key)
                if not entry:
                    self.__disconnect()
                    time.sleep(process_sleep)
                    continue
                # we are blacklisted by afrinic...
                if self.server == 'whois.afrinic.net':
                    whois = 'we are blacklisted by afrinic...'
                    self.cache_db.set(entry, self.server + '\n' + unicode(whois,  errors="replace"))
                    continue
#                if self.server == 'whois.apnic.net':
#                    whois = 'we are probably blacklisted by apnic...'
#                    self.cache_db.set(entry, self.server + '\n' + unicode(whois,  errors="replace"))
#                    continue
                if self.cache_db.get(entry) is None:
                    if not self.connected:
                        self.__connect()
                    syslog.syslog(syslog.LOG_DEBUG, self.server + ", query : " + str(entry))
                    whois = self.fetcher.fetch_whois(entry, self.keepalive)
                    if whois == '':
                        self.temp_db.rpush(self.key, entry)
                    else:
                        self.cache_db.set(entry, self.server + '\n' + unicode(whois,  errors="replace"))
                        self.cache_db.expire(entry, cache_ttl)
                    if not self.keepalive:
                        self.__disconnect()
            except IOError, e:
                if e.errno == errno.ETIMEDOUT:
                    self.temp_db.push(self.server,entry)
                    syslog.syslog(syslog.LOG_ERR, "timeout on " + self.server)
                    self.connected = False
                elif e.errno == errno.EPIPE:
                    self.temp_db.push(self.server,entry)
                    syslog.syslog(syslog.LOG_ERR, "Broken pipe " + self.server)
                    self.connected = False
                elif e.errno == errno.ECONNRESET:
                    self.temp_db.push(self.server,entry)
                    syslog.syslog(syslog.LOG_ERR, "Reset by peer:  " + self.server)
                    self.connected = False
                elif e.errno == errno.ECONNREFUSED:
                    self.temp_db.push(self.server,entry)
                    syslog.syslog(syslog.LOG_ERR, "Connexion refused by peer:  " + self.server)
                    self.connected = False
                    time.sleep(process_sleep)
                else:
                    raise IOError(e)
