#!/usr/bin/python

"""
Quick and durty code computing reports based on the information found in the database. 
"""


import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.optionxform = str
config_file = "/path/to/bgp-ranking.conf"
config.read(config_file)
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

from whois_parser.bgp_parsers import *

import time
import redis
import IPy

import datetime

routing_db = redis.Redis(port = int(config.get('redis','port_cache')) , db=config.get('redis','routing'))
global_db  = redis.Redis(port = int(config.get('redis','port_master')), db=config.get('redis','global'))
history_db = redis.Redis(port = int(config.get('redis','port_master')), db=config.get('redis','history'))

class Ranking():
    separator = config.get('input_keys','separator')
    
    def __init__(self):
        self.weight = {}
        self.date = None
    
    #def rank_and_save(self, asn, date = datetime.date.today()):
        #self.date = date.isoformat()
        #self.asn = asn
        #self.sources = global_db.smembers('{date}{sep}{key}'.format(date = date.isoformat(), sep = self.separator, key = config.get('redis','index_sources')))
        #self.ip_count()
        #self.make_index()
        #self.rank()
        #self.make_history()
        
    #def update_asn_list(self):
        #if self.date is None:
            #self.date = datetime.date.today().isoformat()
        #sources = global_db.smembers('{date}{sep}{key}'.format(date = self.date, sep = self.separator, \
                                        #key = config.get('input_keys','index_sources')))
        #self.asn_details = {}
        #for source in sources:
            #index_day_asns_details = '{date}{sep}{source}{sep}{key}'.format(sep = self.separator, \
                                        #date=self.date, source=source, \
                                        #key=config.get('input_keys','index_asns_details'))
            #self.asn_details[source] = global_db.smembers(index_day_asns_details)

    def rank_using_key(self, key):
        if key is not None:
            self.asn, self.timestamp, self.date, self.source = key.split(self.separator)
            self.ip_count()
            self.make_index_source()
            self.rank()
            self.make_history()

    def ip_count(self):
        keys = [str(self.asn) + ':v4', str(self.asn) + ':v6']
        self.ipv4, self.ipv6 = routing_db.mget(keys)
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
            routing_db.mset({keys[0]: self.ipv4, keys[1]: self.ipv6})
        else:
            self.ipv4 = int(self.ipv4)
            self.ipv6 = int(self.ipv6)

    def make_index_source(self):
        ips = global_db.smembers('{asn}{sep}{timestamp}{sep}{date}{sep}{source}'.format(sep = self.separator, \
                                        asn = self.asn, timestamp = self.timestamp, date = self.date, source = self.source))
        self.weight = [0.0,0.0]
        for i in ips:
            ip_extract, timestamp = i.split(self.separator)
            ip = IPy.IP(ip_extract)
            if ip.version() == 6:
                self.weight[1] += 1.0
            else :
                self.weight[0] += 1.0

    def rank(self):
        self.rank_by_source = [0.0, 0.0]
        if self.ipv4 > 0 :
            self.rank_by_source[0] = (float(self.weight[0])/self.ipv4)
        elif self.ipv6 > 0 :
            self.rank_by_source[1] = (float(self.weight[1])/self.ipv6)
    
    def make_history(self):
        # FIXME pipeline?
        if self.rank_by_source[0] > 0.0:
            asn_key_v4_details = '{asn}{sep}{date}{sep}{source}{sep}{v4}{sep}{details}'.format(sep = self.separator, asn = self.asn, \
                                    date = self.date, source = self.source, v4 = config.get('input_keys','rankv4'), \
                                    details = config.get('input_keys','daily_asns_details'))

            history_db.zadd(asn_key_v4_details, self.timestamp, self.rank_by_source[0])
            
            asn_key_v4 = '{asn}{sep}{date}{sep}{source}{sep}{v4}'.format(sep = self.separator, asn = self.asn, \
                            date = self.date, source = self.source, v4 = config.get('input_keys','rankv4'))

            temp_rank = history_db.get(asn_key_v4)
            if temp_rank is not None:
                temp_rank = float(temp_rank) + self.rank_by_source[0]
            else:
                temp_rank = self.rank_by_source[0]
            history_db.set(asn_key_v4, temp_rank)

        if self.rank_by_source[1] > 0.0:
            asn_key_v6_details = '{asn}{sep}{date}{sep}{source}{sep}{v6}{sep}{details}'.format(sep = self.separator, asn = self.asn, \
                                    date = self.date, source = self.source, v6 = config.get('input_keys','rankv6'), \
                                    details = config.get('input_keys','daily_asns_details'))

            history_db.zadd(asn_key_v6_details, self.timestamp, self.rank_by_source[1])

            asn_key_v6 = '{asn}{sep}{date}{sep}{source}{sep}{v6}'.format(sep = self.separator, asn = self.asn, \
                            date = self.date, source = self.source, v6 = config.get('input_keys','rankv6'))

            temp_rank = history_db.get(asn_key_v6)
            if temp_rank is not None:
                temp_rank = float(temp_rank) + self.rank_by_source[1]
            else:
                temp_rank = self.rank_by_source[1]
            history_db.set(asn_key_v6, temp_rank)
