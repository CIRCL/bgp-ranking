#!/usr/bin/python
# -*- coding: utf-8 -*-
import redis
from whois_fetcher import *
import errno

# query keys, ris for ris queries, whois for whois queries 
redis_keys = ['ris', 'whois']
# Temporary redis database, used to push ris and whois requests
temp_reris_db = 0
# Cache redis database, used to set ris responses
ris_cache_reris_db = 1
# Cache redis database, used to set whois responses
whois_cache_reris_db = 2

# In case there is nothing to fetch, the process will sleep 5 seconds 
process_sleep = 5

# Set the ttl of the cached entries to 1 day 
cache_ttl = 86400

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
            self.key = redis_keys[0]
        else:
            self.key = self.server
            self.cache_db = redis.Redis(db=whois_cache_reris_db)
        if self.server in self.support_keepalive:
            self.keepalive = True
        self.fetcher = WhoisFetcher(get_server_by_name\
                            (unicode(self.server)))
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
#                print(self.server + ', llen: ' + str(self.redis_instance.llen(self.key)))
                entry = self.temp_db.pop(self.key)
                if not entry:
                    self.__disconnect()
                    time.sleep(process_sleep)
                    continue
                # we are blacklisted by afrinic...
                if self.server == 'whois.afrinic.net':
                    whois = 'we are blacklisted by afrinic...'
                    self.cache_db.set(entry, self.server + '\n' + unicode(whois,  errors="replace"))
                    continue
                if self.server == 'whois.apnic.net':
                    whois = 'we are probably blacklisted by apnic...'
                    self.cache_db.set(entry, self.server + '\n' + unicode(whois,  errors="replace"))
                    continue
                if not self.cache_db.get(entry):
                    if not self.connected:
                        self.__connect()
#                    print(self.server + ", query : " + str(entry))
                    whois = self.fetcher.fetch_whois(entry, self.keepalive)
                    if whois == '':
                        self.temp_db.push(self.key, entry)
                    else:
                        self.cache_db.set(entry, self.server + '\n' + unicode(whois,  errors="replace"))
                        self.cache_db.expire(entry, cache_ttl)
                    if not self.keepalive:
                        self.__disconnect()
            except IOError, e:
                if e.errno == errno.ETIMEDOUT:
                    self.temp_db.push(self.server,entry)
                    print("timeout on " + self.server)
                    self.connected = False
                elif e.errno == errno.EPIPE:
                    self.temp_db.push(self.server,entry)
                    print("Broken pipe " + self.server)
                    self.connected = False
                elif e.errno == errno.ECONNRESET:
                    self.temp_db.push(self.server,entry)
                    print("Reset by peer:  " + self.server)
                    self.connected = False
                elif e.errno == errno.ECONNREFUSED:
                    self.temp_db.push(self.server,entry)
                    print("Connexion refused by peer:  " + self.server)
                    self.connected = False
                    time.sleep(process_sleep)
                else:
                    raise IOError(e)
