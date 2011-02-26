# -*- coding: utf-8 -*-
"""
    bgp_ranking.lib.InsertRIS
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Insert the RIS Whois information in the database. 

    :copyright: Copyright 2010-2011 by the BGP Ranking team, see AUTHORS.
    :license: AGPL3, see LICENSE for details.
"""

from whois_parser.whois_parsers import *

import syslog
import datetime
syslog.openlog('BGP_Ranking_Fetching_RIS', syslog.LOG_PID, syslog.LOG_USER)

import re

import redis
import time
import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config_file = "/path/to/bgp-ranking.conf"
config.read(config_file)
root_dir = config.get('directories','root') 
sleep_timer = int(config.get('sleep_timers','short'))

import dateutil.parser


# Temporary redis database, used to push ris and whois requests
temp_reris_db = int(config.get('redis','temp'))
# Cache redis database, used to set ris responses
ris_cache_reris_db = int(config.get('redis','cache_ris'))
# Global redis database, used to save all the information
global_db = config.get('redis','global')

class InsertRIS():
    """
    Generate a ASNsDescriptions to all IPsDescriptions wich do not already have one.
    
    Take a look at doc/uml-diagramms/RIS\ Fetching.png to see a diagramm.
    """
    default_asn_desc = None
    max_consecutive_errors = 5
    
    separator = config.get('input_keys','separator')
    
    default_asn = config.get('modules_global','default_asn')
    
    key_asn = config.get('input_keys','asn')
    key_owner = config.get('input_keys','owner')
    key_ips_block = config.get('input_keys','ips_block')

    def __init__(self):
        """
        Initialize the two connectors to the redis server 
        """        
        self.cache_db_ris = redis.Redis(port = int(config.get('redis','port_cache')), db=ris_cache_reris_db)
        self.temp_db = redis.Redis(db=temp_reris_db)
        self.global_db = redis.Redis(db=global_db)
        default_asn_members = self.global_db.smembers(config.get('modules_global','default_asn'))
        if len(default_asn_members) == 0 :
            self.default_asn_key = self.add_asn_entry(\
                                    config.get('modules_global','default_asn'), \
                                    config.get('modules_global','default_asn_descr'), \
                                    config.get('modules_global','default_asn_route'))
        else:
            self.default_asn_key = '{asn}{sep}{tstamp}'.format(asn=config.get('modules_global','default_asn'), sep = self.separator, tstamp=default_asn_members.pop())

    def add_asn_entry(self, asn, owner, ips_block):
        key = None
        asn_timestamps = self.global_db.smembers(asn)
        key_list = []
        for asn_timestamp in asn_timestamps:
            temp_key = "{asn}{sep}{timestamp}".format(asn=asn, sep = self.separator, timestamp=asn_timestamp)
            key_list.append("{key}{sep}{ips_block}".format(key = temp_key, sep = self.separator, ips_block = self.key_ips_block))
        ips_blocks = []
        if len(key_list) != 0:
            ips_blocks = self.global_db.mget(key_list)
        i = 0 
        for block in ips_blocks:
            if block == ips_block:
                asn, timestamp, b = key_list[i].split(self.separator)
                temp_key = "{asn}{sep}{timestamp}".format(asn=asn, sep = self.separator, timestamp=timestamp)
                if self.global_db.get("{key}{sep}{owner}".format(key = temp_key, sep = self.separator, owner = self.key_owner)) == owner:
                    key = temp_key
                    break
            i += 1
        if key is None:
            timestamp = datetime.datetime.utcnow().isoformat()
            key = "{asn}{sep}{timestamp}".format(asn=asn, sep = self.separator, timestamp=timestamp)
            to_set = {  "{key}{sep}{owner}"     .format(key = key, sep = self.separator, owner = self.key_owner)        : owner, 
                        "{key}{sep}{ips_block}" .format(key = key, sep = self.separator, ips_block = self.key_ips_block): ips_block}
            pipeline = self.global_db.pipeline(False)
            pipeline.sadd(asn, timestamp)
            pipeline.mset(to_set)
            pipeline.execute()
        return key

    def __update_db_ris(self, data):
        """ 
        Update the database with the RIS whois informations and return the corresponding entry
        """
        splitted = data.partition('\n')
        ris_origin = splitted[0]
        riswhois = splitted[2]
        ris_whois = Whois(riswhois,  ris_origin)
        if not ris_whois.origin:
            #self.global_db.set("{ip_info}{sep}{key}".format(ip_info = description, sep = self.separator, key = self.key_asn), self.default_asn_key)
            return self.default_asn_key
        else:
            asn_key = self.add_asn_entry(ris_whois.origin, ris_whois.description, ris_whois.route)
            #self.global_db.set("{ip_info}{sep}{key}".format(ip_info = description, sep = self.separator, key = self.key_asn), asn_key)
            return asn_key

    def get_ris(self):
        """
        Get the RIS whois information on a particular interval and put it into redis
        """
        key_no_asn = config.get('redis','no_asn')
        errors = 0 
        to_return = False
        i = 0 
        while True:
            sets = self.global_db.smembers(key_no_asn)
            if len(sets) == 0:
                break
            to_return = True
            for ip_set in sets:
                errors = 0 
                ip_set_card = self.global_db.scard(ip_set)
                if ip_set_card == 0:
                    self.global_db.srem(key_no_asn, ip_set)
                    continue
                for i in range(ip_set_card):
                    temp, date, source, key = ip_set.split(self.separator)
                    ip_details = self.global_db.spop(ip_set)
                    if ip_details is None:
                        break
                    ip, timestamp = ip_details.split(self.separator)
                    entry = self.cache_db_ris.get(ip)
                    if entry is None:
                        errors += 1
                        self.global_db.sadd(ip_set, ip_details)
                        if errors >= self.max_consecutive_errors:
                            self.temp_db.sadd(config.get('redis','key_temp_ris'), ip)
                    else:
                        errors = 0
                        asn = self.__update_db_ris(entry)
                        date = dateutil.parser.parse(timestamp).date().isoformat()
                        index_day_asns_details = '{date}{sep}{source}{sep}{key}'.format(sep = self.separator, \
                                                        date=date, source=source, \
                                                        key=config.get('input_keys','index_asns_details'))
                        index_day_asns = '{date}{sep}{source}{sep}{key}'.format(sep = self.separator, \
                                                        date=date, source=source, \
                                                        key=config.get('input_keys','index_asns'))
                        index_as_ips = '{asn}{sep}{date}{sep}{source}'.format(sep = self.separator, asn = asn,\
                                                        date=date, source=source)
                        if self.global_db.sismember(index_as_ips, ip_details) is False:
                            self.global_db.sadd(index_day_asns_details, asn)
                            self.global_db.sadd(index_day_asns, asn.split(self.separator)[0])
                            self.global_db.sadd(index_as_ips, ip_details)
                            to_return = True
                syslog.syslog(syslog.LOG_DEBUG, str(self.global_db.scard(ip_set)) + ' RIS Whois to insert on ' + ip_set)
            time.sleep(sleep_timer)
        return to_return
