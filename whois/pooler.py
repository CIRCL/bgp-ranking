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
    
    def kill_all(self):
        self.kill_sorters()
        self.kill_connectors()
    
    def kill_sorters(self):
        for sorter in self.whois_sorters:
            sorter.terminate()
    
    def kill_connectors(self):
        for server, processes in self.whois_connectors.iteritems():
            for process in processes:
                process.terminate()
    
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
