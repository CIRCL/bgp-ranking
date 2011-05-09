#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Ranking
    ~~~~~~~
    
    Compute the ranking of a subnet given as parameter
"""
import os 
import sys
import ConfigParser

import time
import redis
import IPy

import datetime

class Ranking(object):
    """
        This class is used in a big loop on each subnet we want to rank.
    """
    
    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.optionxform = str
        config_file = "/path/to/bgp-ranking.conf"
        self.config.read(config_file)
        
        self.routing_db = redis.Redis(port = int(self.config.get('redis','port_cache')) , db=self.config.get('redis','routing'))
        self.global_db  = redis.Redis(port = int(self.config.get('redis','port_master')), db=self.config.get('redis','global'))
        self.history_db = redis.Redis(port = int(self.config.get('redis','port_master')), db=self.config.get('redis','history'))
        self.separator = self.config.get('input_keys','separator')
        self.weight = {}
        self.date = None

    def rank_using_key(self, key):
        """
            The key is the subnet we want to rank
        """
        if key is not None:
            self.asn, self.timestamp, self.date, self.source = key.split(self.separator)
            self.ip_count()
            self.make_index_source()
            self.rank()
            self.make_history()

    def ip_count(self):
        """
            Count the number of IPs announced by the ASN (ipv6 and ipv4)
        """
        
        keys = [str(self.asn) + ':v4', str(self.asn) + ':v6']
        self.ipv4, self.ipv6 = self.routing_db.mget(keys)
        if self.ipv4 is None or self.ipv6 is None:
            blocks = self.routing_db.smembers(self.asn)
            self.ipv4 = 0
            self.ipv6 = 0
            for block in blocks:
                ip = IPy.IP(block)
                if ip.version() == 6:
                    self.ipv6 += ip.len()
                else :
                    self.ipv4 += ip.len()
            self.routing_db.mset({keys[0]: self.ipv4, keys[1]: self.ipv6})
        else:
            self.ipv4 = int(self.ipv4)
            self.ipv6 = int(self.ipv6)

    def make_index_source(self):
        """
            Count the number of IPs found in the dataset for this subnet
        """
        ips = self.global_db.smembers('{asn}{sep}{timestamp}{sep}{date}{sep}{source}'.format(sep = self.separator, \
                                        asn = self.asn, timestamp = self.timestamp, date = self.date, source = self.source))
        self.weight = [0.0,0.0]
        for i in ips:
            ip_extract, timestamp = i.split(self.separator)
            ip = IPy.IP(ip_extract)
            if ip.version() == 4:
                self.weight[0] += 1.0
            else :
                self.weight[1] += 1.0

    def rank(self):
        """
            Divide the number of IPs in the datasets by the total announced by the AS
        """
        self.rank_by_source = [0.0, 0.0]
        if self.ipv4 > 0 :
            self.rank_by_source[0] = (float(self.weight[0])/self.ipv4)
        elif self.ipv6 > 0 :
            self.rank_by_source[1] = (float(self.weight[1])/self.ipv6)
    
    def make_history(self):
        """
            Save the ranks (by subnets and global) in the database.
        """
        if self.rank_by_source[0] > 0.0:
            asn_key_v4_details = '{asn}{sep}{date}{sep}{source}{sep}{v4}{sep}{details}'\
                                    .format(sep = self.separator, \
                                            asn = self.asn, \
                                            date = self.date, source = self.source, \
                                            v4 = self.config.get('input_keys','rankv4'), \
                                            details = self.config.get('input_keys','daily_asns_details'))

            self.history_db.zadd(asn_key_v4_details, self.timestamp, self.rank_by_source[0])
            
            asn_key_v4 = '{asn}{sep}{date}{sep}{source}{sep}{v4}'.format(sep = self.separator, asn = self.asn, \
                            date = self.date, source = self.source, v4 = self.config.get('input_keys','rankv4'))

            temp_rank = self.history_db.get(asn_key_v4)
            if temp_rank is not None:
                temp_rank = float(temp_rank) + self.rank_by_source[0]
            else:
                temp_rank = self.rank_by_source[0]
            self.history_db.set(asn_key_v4, temp_rank)

        if self.rank_by_source[1] > 0.0:
            asn_key_v6_details = '{asn}{sep}{date}{sep}{source}{sep}{v6}{sep}{details}'.format(sep = self.separator, asn = self.asn, \
                                    date = self.date, source = self.source, v6 = self.config.get('input_keys','rankv6'), \
                                    details = self.config.get('input_keys','daily_asns_details'))

            self.history_db.zadd(asn_key_v6_details, self.timestamp, self.rank_by_source[1])

            asn_key_v6 = '{asn}{sep}{date}{sep}{source}{sep}{v6}'.format(sep = self.separator, asn = self.asn, \
                            date = self.date, source = self.source, v6 = self.config.get('input_keys','rankv6'))

            temp_rank = self.history_db.get(asn_key_v6)
            if temp_rank is not None:
                temp_rank = float(temp_rank) + self.rank_by_source[1]
            else:
                temp_rank = self.rank_by_source[1]
            self.history_db.set(asn_key_v6, temp_rank)
