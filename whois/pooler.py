#!/usr/bin/python
# -*- coding: utf-8 -*-

from whois_fetcher import *
redis_keys = ['ris', 'whois']


import redis
import time

from multiprocessing import Process

def start_all():
    Process(target=start_RIS_connector).start()
    Process(target=whois_sort).start()

def start_RIS_connector():
    RISConnector().launch()

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
            if self.redis_instance.llen(self.key) == 0:
                self.__disconnect()
                time.sleep(5)
                continue
            if not self.connected:
                self.__connect()
            ip = self.redis_instance.pop(self.key)
            whois = self.fetcher.fetch_whois(ip,  True)
            self.redis_instance.set(ip, whois)

def whois_sort():
    existing_whois_connectors = []
    redis_instance = redis.Redis()
    key = redis_keys[1]
    while 1:
        bloc = redis_instance.pop(key)
        if not bloc:
            time.sleep(5)
            continue
        server = get_server_by_query(bloc)
        if not server:
            print ("error: " + bloc)
            continue
        redis_instance.push(server.whois,  bloc)
        if server.whois not in existing_whois_connectors:
            existing_whois_connectors.append(server.whois)
            Process(target=start_connector, args=(server.whois,)).start()


class Connector(object):
    keepalive = False
    support_keepalive = ['whois.ripe.net']
    
    def __init__(self, server):
        self.redis_instance = redis.Redis(db=0)
        self.server = server
        if self.server in self.support_keepalive:
            self.keepalive = True
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
            if self.redis_instance.llen(self.server) == 0:
                self.__disconnect()
                time.sleep(1)
                continue
            ip = self.redis_instance.pop(self.server)
            if not self.redis_instance.get(ip):
                if not self.connected:
                    self.__connect()
                print(self.server + ": " + ip)
                whois = self.fetcher.fetch_whois(ip, self.keepalive)
                self.redis_instance.set(ip, [self.server, whois])
                if not self.keepalive:
                    self.__disconnect()

def start_connector(server):
    Connector(server).launch()
