#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This class is a little bit complicated, take a look in 
doc/uml-diagramms/{Whois\ Fetching.png,RIS\ Fetching.png} 
for more informations
"""

from whois_fetcher import *
redis_keys = ['ris', 'whois']

process_sleep = 5


import redis
import time

from multiprocessing import Process

class Pooler():
    existing_riswhois_connectors = []
    existing_whois_connectors = {}
    whois_connectors_by_server = 1

    def start_all(self):
        Process(target=self.__start_RIS_connector).start()
        Process(target=self.__whois_sort).start()

    def __start_RIS_connector(self):
        Connector('riswhois.ripe.net',  True).launch()

    def __start_connector(self, server):
        Connector(server).launch()

    def __whois_sort(self):
        redis_instance = redis.Redis(db=0)
        key = redis_keys[1]
        while 1:
            print('blocs to whois: ' + str(redis_instance.llen(key)))
            bloc = redis_instance.pop(key)
            if not bloc:
                time.sleep(process_sleep)
                continue
            server = get_server_by_query(bloc)
            if not server:
                print ("error, no server found for this block : " + bloc)
                redis_instance.push(key, block)
                continue
            print('connect to server: ' + server.whois)
            redis_instance.push(server.whois,  bloc)
            if not self.existing_whois_connectors.get(server.whois,  None):
                self.existing_whois_connectors[server.whois] = []
                self.__launch_whois_connectors(server.whois)
            print(self.existing_whois_connectors)
        print('WARNING, GONE FROM __whois_sort')
    
    def __launch_whois_connectors(self,  server):
        print('Connectors starting: ' + server)
        it = 0
        while it < self.whois_connectors_by_server:
            it +=1 
            p = Process(target=self.__start_connector, args=(server,))
            self.existing_whois_connectors[server].append(p)
            p.start()
        print('Connectors started: ' + server)

class Connector(object):
    """
    Make queries to Whois 
    """
    keepalive = False
    support_keepalive = ['riswhois.ripe.net', 'whois.ripe.net']
    
    def __init__(self, server,  ris = False):
        self.redis_instance = redis.Redis(db=0)
        self.server = server
        self.ris = ris
        if self.ris:
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
                print(self.server + ', llen: ' + str(self.redis_instance.llen(self.key)))
                entry = self.redis_instance.pop(self.key)
                if not entry:
                    self.__disconnect()
                    time.sleep(process_sleep)
                    continue
                if not self.redis_instance.get(entry):
                    if not self.connected:
                        self.__connect()
                    print(self.server + ", query : " + str(entry))
                    whois = self.fetcher.fetch_whois(entry, self.keepalive)
                    if self.ris:
                        self.redis_instance.set(entry, unicode(whois,  errors="replace"))
                    else : 
                        self.redis_instance.set(entry, self.server + '\n' + unicode(whois,  errors="replace"))
                    if not self.keepalive:
                        self.__disconnect()
            except IOError, e:
                if e.errno == errno.ETIMEDOUT:
                    self.redis_instance.push(self.server,entry)
                    print("timeout on " + self.server)
                    self.connected = False
                else:
                    raise IOError(e)
                    



class RISConnector(object):
    """
    Make queries to RIS Whois 
    """
    key = redis_keys[0]
    server = 'riswhois.ripe.net'
    
    def __init__(self):
        self.redis_instance = redis.Redis(db=0)
        self.fetcher = WhoisFetcher(get_server_by_name\
                            (unicode(self.server)))
    
    def __connect(self):
        self.fetcher.connect()   
        self.connected = True

    def __disconnect(self):
        self.fetcher.disconnect()
        self.connected = False
    
    def launch(self):
        self.__connect()
        while 1:
            print(self.server + ', llen: ' + str(self.redis_instance.llen(self.key)))
            ip = self.redis_instance.pop(self.key)
            if not ip :
                self.__disconnect()
                time.sleep(1)
                continue
            if not self.redis_instance.get(ip):
                if not self.connected:
                    self.__connect()
                whois = self.fetcher.fetch_whois(ip,  True)
                self.redis_instance.set(ip, unicode(whois,  errors="replace"))
