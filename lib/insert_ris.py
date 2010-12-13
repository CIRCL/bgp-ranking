# -*- coding: utf-8 -*-

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
config.read("../bgp-ranking.conf")
root_dir = config.get('directories','root') 
sleep_timer = int(config.get('sleep_timers','short'))

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
    max_consecutive_errors = 10
    
    separator = config.get('input_keys','separator')
    
    default_asn = config.get('modules_global','default_asn')
    
    key_asn = config.get('input_keys','asn')
    key_owner = config.get('input_keys','owner')
    key_ips_block = config.get('input_keys','ips_block')

    def __init__(self):
        """
        Initialize the two connectors to the redis server 
        """        
        self.cache_db_ris = redis.Redis(db=ris_cache_reris_db)
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
        for asn_timestamp in asn_timestamps:
            temp_key = "{asn}{sep}{timestamp}".format(asn=asn, sep = self.separator, timestamp=asn_timestamp)
            if self.global_db.get("{key}{sep}{owner}".format(key = temp_key, sep = self.separator, owner = self.key_owner)) == owner and \
                self.global_db.get("{key}{sep}{ips_block}".format(key = temp_key, sep = self.separator, ips_block = self.key_ips_block)) == ips_block:
                key = temp_key
                break
        if key is None:
            timestamp = datetime.datetime.utcnow().isoformat()
            self.global_db.sadd(asn, timestamp)
            key = "{asn}{sep}{timestamp}".format(asn=asn, sep = self.separator, timestamp=timestamp)
            self.global_db.set("{key}{sep}{owner}".format(key = key, sep = self.separator, owner = self.key_owner), owner)
            self.global_db.set("{key}{sep}{ips_block}".format(key = key, sep = self.separator, ips_block = self.key_ips_block), ips_block)
        return key

    def __update_db_ris(self, description,  data):
        """ 
        Update the database with the RIS whois informations and return the corresponding entry
        """
        splitted = data.partition('\n')
        ris_origin = splitted[0]
        riswhois = splitted[2]
        ris_whois = Whois(riswhois,  ris_origin)
        if not ris_whois.origin:
            self.global_db.set("{ip_info}{sep}{key}".format(ip_info = description, sep = self.separator, key = self.key_asn), self.default_asn_key)
            return self.default_asn_key
        else:
            asn_key = self.add_asn_entry(ris_whois.origin, ris_whois.description, ris_whois.route)
            self.global_db.set("{ip_info}{sep}{key}".format(ip_info = description, sep = self.separator, key = self.key_asn), asn_key)
            return asn_key

    def get_ris(self):
        """
        Get the RIS whois information on a particular interval and put it into redis
        """
        key_no_asn = config.get('redis','no_asn')
        description = self.global_db.spop(key_no_asn)
        errors = 0 
        to_return = False
        i = 0 
        while description is not None:
            ip, timestamp, date, source = description.split(self.separator)
            entry = self.cache_db_ris.get(ip)
            if entry is None:
                errors += 1
                self.global_db.sadd(key_no_asn, description)
                if errors >= self.max_consecutive_errors:
                    self.temp_db.sadd(config.get('redis','key_temp_ris'), ip)
                    break
            else:
                i += 1
                errors = 0
                asn = self.__update_db_ris(description, entry)
                index_day_asns = '{date}{sep}{source}{sep}{key}'.format(sep = self.separator, date=datetime.date.today().isoformat(), source=source, \
                                                                        key=config.get('input_keys','index_asns'))
                index_as_ips = '{asn}{sep}{date}{sep}{source}'.format(sep = self.separator, asn = asn, date=datetime.date.today().isoformat(), source=source)
                self.global_db.sadd(index_day_asns, asn)
                self.global_db.sadd(index_as_ips, description)
                to_return = True
            if i >= 1000:
                syslog.syslog(syslog.LOG_DEBUG, 'RIS Whois to fetch: ' + str(self.global_db.scard(key_no_asn)))
                i = 0 
            description = self.global_db.spop(key_no_asn)
        return to_return
