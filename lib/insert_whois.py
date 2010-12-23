# -*- coding: utf-8 -*-

import syslog
syslog.openlog('BGP_Ranking_Fetching_Whois', syslog.LOG_PID, syslog.LOG_USER)

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
# Cache redis database, used to set whois responses
whois_cache_reris_db = int(config.get('redis','cache_whois'))
# Global redis database, used to save all the information
global_db = config.get('redis','global')

class InsertWhois():
    """
    Set the whois information to ASNsDescriptions wich do not already have one.
    
    Take a look at doc/uml-diagramms/Whois\ Fetching.png to see a diagramm.
    """
    max_consecutive_errors = 10
    
    separator = config.get('input_keys','separator')
    
    key_whois = config.get('input_keys','whois')
    key_whois_server = config.get('input_keys','whois_server')
    

    def __init__(self):
        """
        Initialize the two connectors to the redis server 
        """
        self.cache_db_whois = redis.Redis(port = config.get('redis','port_cache'), db=whois_cache_reris_db)
        self.temp_db = redis.Redis(db=temp_reris_db)
        self.global_db = redis.Redis(db=global_db)

    def get_whois(self):
        """
        Get the Whois information on a particular interval and put it into redis
        """
        key_no_asn = config.get('redis','no_whois')
        description = self.global_db.spop(key_no_whois)
        errors = 0 
        to_return = False
        
        while description is not None:
            ip, timestamp = description.split(self.separator)
            entry = self.cache_db_whois.get(ip)
            if entry is None:
                errors += 1
                self.global_db.sadd(key_no_whois, description)
                if errors >= self.max_consecutive_errors:
                    break
            else:
                errors = 0
                splitted = entry.partition('\n')
                whois_server = splitted[0]
                whois = splitted[2]
                # FIXME: add TTL ? 
                self.global_db.set("{entry}{sep}{whois_server}".format(entry = entry,sep = self.separator, whois_server = self.key_whois_server), whois_server)
                self.global_db.set("{entry}{sep}{whois}".format(entry = entry,sep = self.separator, whois = self.key_whois), whois)
                to_return = True
            description = self.global_db.spop(key_no_asn)
        syslog.syslog(syslog.LOG_DEBUG, 'Whois to fetch: ' + str(self.global_db.scard(key_no_whois)))
        return to_return
