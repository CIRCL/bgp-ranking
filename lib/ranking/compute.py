#!/usr/bin/python

"""
Quick and durty code computing reports based on the information found in the database. 
"""


import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.optionxform = str
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

from whois_parser.bgp_parsers import *

import time
import redis
import IPy

import datetime

routing_db = redis.Redis(db=config.get('redis','routing'))
global_db = redis.Redis(db=config.get('redis','global'))
history_db = redis.Redis(db=config.get('redis','history'))

class Ranking():
    separator = config.get('input_keys','separator')
    
    def __init__(self):
        self.weight = {}
    
    #def rank_and_save(self, asn, date = datetime.date.today()):
        #self.date = date.isoformat()
        #self.asn = asn
        #self.sources = global_db.smembers('{date}{sep}{key}'.format(date = date.isoformat(), sep = self.separator, key = config.get('redis','index_sources')))
        #self.ip_count()
        #self.make_index()
        #self.rank()
        #self.make_history()

    def rank_using_key(self, key):
        if key is not None:
            self.asn, self.timestamp, self.date, source = key.split(self.separator)
            self.ip_count()
            self.make_index_source(source)
            self.rank()
            self.make_history()

    def ip_count(self):
        keyv4 = str(self.asn) + ':v4'
        keyv6 = str(self.asn) + ':v6'
        self.ipv4 = routing_db.get(keyv4)
        self.ipv6 = routing_db.get(keyv6)
        if self.ipv4 is None or self.ipv6 is None:
            blocks = routing_db.smembers(self.asn)
            self.ipv4 = 0
            self.ipv6 = 0
            for block in blocks:
                ip = IPy.IP(block)
                if ip.version() == 6:
                    self.ipv6 += ip.len()
                else :
                    self.ipv4 += ip.len()
            routing_db.set(keyv4, self.ipv4)
            routing_db.set(keyv6, self.ipv6)
        else:
            self.ipv4 = int(self.ipv4)
            self.ipv6 = int(self.ipv6)

    def make_index(self):
        asn_sources = {}
        for source in self.sources:
            self.make_index_source(source)

    def make_index_source(self, source):
        ips = global_db.smembers('{asn}{sep}{timestamp}{sep}{date}{sep}{source}'.format(sep = self.separator, \
                                        asn = self.asn, timestamp = self.timestamp, date = self.date, source = source))
        self.weight[str(source)] = [0.0,0.0]
        for i in ips:
            ip_extract, timestamp = i.split(self.separator)
            ip = IPy.IP(ip_extract)
            if ip.version() == 6:
                self.weight[str(source)][1] += 1.0
            else :
                self.weight[str(source)][0] += 1.0

    def rank(self):
        self.rank_by_source = {}
        for key in self.weight:
            self.rank_by_source[key] = [0.0, 0.0]
            if self.ipv4 > 0 :
                self.rank_by_source[key][0] = (float(self.weight[key][0])/self.ipv4)
            elif self.ipv6 > 0 :
                self.rank_by_source[key][1] = (float(self.weight[key][1])/self.ipv6)
    
    def make_history(self):
        asn_key_v4 = '{asn}{sep}{date}{sep}{source}{sep}{v4}'.format(sep = self.separator, asn = self.asn, \
                        date = self.date, source = key, v4 = config.get('input_keys','rankv4'))
        asn_key_v6 = '{asn}{sep}{date}{sep}{source}{sep}{v6}'.format(sep = self.separator, asn = self.asn, \
                        date = self.date, source = key, v6 = config.get('input_keys','rankv6'))
        history_db.delete(asn_key_v4, asn_key_v6)
        for key in self.rank_by_source:
            if self.rank_by_source[key][0] > 0.0:
                history_db.set('{asn}{sep}{timestamp}{sep}{date}{sep}{source}{sep}{v4}'.format(sep = self.separator, \
                                    asn = self.asn, timestamp = self.timestamp, date = self.date, source = key, \
                                    v4 = config.get('input_keys','rankv4')), self.rank_by_source[key][0])
                history_db.incr(asn_key_v4, self.rank_by_source[key][0])
            if self.rank_by_source[key][1] > 0.0:
                history_db.set('{asn}{sep}{timestamp}{sep}{date}{sep}{source}{sep}{v6}'.format(sep = self.separator, \
                                                asn = self.asn, timestamp = self.timestamp, date = self.date, source = key, \
                                                v6 = config.get('input_keys','rankv6')), self.rank_by_source[key][1])
                history_db.incr(asn_key_v6, self.rank_by_source[key][1])
