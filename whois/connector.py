#!/usr/bin/python
# -*- coding: utf-8 -*-
import redis
from whois_fetcher import *
import errno


redis_keys = ['ris', 'whois']
# Temporary redis database, used to push ris and whois requests
temp_reris_db = 0
# Cqche redis database, used to set ris and whois responses
cache_reris_db = 1

process_sleep = 5


class Connector(object):
    """
    Make queries to Whois 
    """
    keepalive = False
    support_keepalive = ['riswhois.ripe.net', 'whois.ripe.net']
    
    def __init__(self, server):
        self.cache_db = redis.Redis(db=cache_reris_db)
        self.temp_db = redis.Redis(db=temp_reris_db)
        self.server = server
        if self.server == 'riswhois.ripe.net':
            self.key = redis_keys[0]
        else:
            self.key = self.server
        if self.server in self.support_keepalive:
            self.keepalive = True
        self.fetcher = WhoisFetcher(get_server_by_name\
                            (unicode(self.server)))
        self.connected = False
    
    def __connect(self):
        self.fetcher.connect()   
        self.connected = True

    def __disconnect(self):
        self.fetcher.disconnect()
        self.connected = False
    
    def launch(self):
        while 1:
            try:
#                print(self.server + ', llen: ' + str(self.redis_instance.llen(self.key)))
                entry = self.temp_db.pop(self.key)
                if not entry:
                    self.__disconnect()
                    time.sleep(process_sleep)
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
                else:
                    raise IOError(e)
