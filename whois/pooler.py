#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
This class is a little bit complicated, take a look in 
doc/uml-diagramms/{Whois\ Fetching.png,RIS\ Fetching.png} 
for more informations
"""

from whois_fetcher import *
redis_keys = ['ris', 'whois']
# Temporary redis database, used to push ris and whois requests
temp_reris_db = 0
# Cqche redis database, used to set ris and whois responses
cache_reris_db = 1

process_sleep = 5


import multiprocessing, logging


import redis
import time

from multiprocessing import Process

class Pooler():
    whois_connectors = {}
    whois_sorters = []
    whois_sorting_processes = 1
    whois_connectors_by_server = 1
    
    def status_all(self):
        self.status_sorters()
        self.status_connectors()
        
    def status_sorters(self):
        print('Status of the sorters processes: ')
        for sorter in self.whois_sorters:
            print(sorter.name + ': ' + str(sorter.is_alive()))
    
    def status_connectors(self):
        for server, processes in self.whois_connectors.iteritems():
            print('status of ' + server + 'connectors: ')
            for process in processes:
                print('\t' + process.name + ': ' + str(process.is_alive()))

    def start_all(self):
        self.__launch_whois_connectors('riswhois.ripe.net')
        self.__launch_whois_sorters()

    def __start_connector(self, server):
        Connector(server).launch()

    def __whois_sort(self):
        logger = multiprocessing.log_to_stderr()
        logger.setLevel(multiprocessing.SUBDEBUG)
        m = multiprocessing.Manager()
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
            if not self.whois_connectors.get(server.whois,  None):
                self.__launch_whois_connectors(server.whois)
    
    def __launch_whois_sorters(self):
        it = 0
        while it < self.whois_sorting_processes:
            it +=1 
            p = Process(target=self.__whois_sort)
            self.whois_sorters.append(p)
            p.start()
        print('Sorters started')

    
    def __launch_whois_connectors(self,  server):
        if not self.whois_connectors.get(server,  None):
            self.whois_connectors[server] = []
            print('Connectors starting: ' + server)
            it = 0
            while it < self.whois_connectors_by_server:
                it +=1 
                p = Process(target=self.__start_connector, args=(server,))
                self.whois_connectors[server].append(p)
                p.start()
            print('Connectors started: ' + server)

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
                else:
                    raise IOError(e)

if __name__ == '__main__':
    p = Pooler()
    p.start_all()
