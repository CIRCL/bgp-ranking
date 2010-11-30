# -*- coding: utf-8 -*-

from whois_parser.whois_parsers import *

import syslog
syslog.openlog('BGP_Ranking_Fetching_RIS', syslog.LOG_PID, syslog.LOG_USER)

import redis
import time
sleep_timer = int(config.get('sleep_timers','short'))

# Temporary redis database, used to push ris and whois requests
temp_reris_db = int(config.get('redis','temp_reris_db'))
# Cache redis database, used to set ris responses
ris_cache_reris_db = int(config.get('redis','ris_cache_reris_db'))
# Global redis database, used to save all the information
global_db = config.get('redis','global_db')

class InsertRIS():
    """
    Generate a ASNsDescriptions to all IPsDescriptions wich do not already have one.
    
    Take a look at doc/uml-diagramms/RIS\ Fetching.png to see a diagramm.
    """
    default_asn_desc = None
    max_consecutive_errors = 10
    
    key_asn = config.get('input_keys','asn')
    key_owner = config.get('input_keys','origin')
    key_ips_block = config.get('input_keys','ips_block')

    def __init__(self):
        """
        Initialize the two connectors to the redis server 
        """        
        self.cache_db_ris = redis.Redis(db=ris_cache_reris_db)
        self.temp_db = redis.Redis(db=temp_reris_db)
        self.global_db = redis.Redis(db=global_db)
        default_asn_members = self.global_db.smembers(config.get('default','asn'))
        if default_asn_members is None:
            self.default_asn_key = self.add_asn_entry('-1', "Default AS, none found using RIS Whois.", "0.0.0.0/0")
        else:
            self.default_asn_key = '%s:%s' % config.get('default','asn'), default_asn_members[0]

    def add_asn_entry(asn, owner, ips_block):
        timestamp = datetime.datetime.utcnow().isoformat()
        key = "%s:%s" % asn, timestamp
        self.global_db.sadd(asn, timestamp)
        self.global_db.set(key + self.key_owner, owner)
        self.global_db.set(key + self.key_ips_block, ips_block)
        return key

    def __update_db_ris(self, current,  data):
        """ 
        Update the database with the RIS whois informations and return the corresponding entry
        """
        splitted = data.partition('\n')
        ris_origin = splitted[0]
        riswhois = splitted[2]
        ris_whois = Whois(riswhois,  ris_origin)
        if not ris_whois.origin:
            self.global_db.set(current + key_asn, self.default_asn)
        else:
            asn_key = self.add_asn_entry(ris_whois.origin, ris_whois.description, ris_whois.route)
            self.global_db.set(current + key_asn, asn_key)

    def get_ris(self):
        """
        Get the RIS whois information on a particular interval and put it into redis
        """
        key_no_asn = config.get('input_keys','no_asn')
        description = self.global_db.pop(key_no_asn)
        errors = 0 
        to_return = False
        
        while description is not None:
            ip, date, source, timestamp = description.split(':')
            entry = self.cache_db_ris.get(ip)
            if entry is None:
                errors += 1
                self.global_db.push(key_no_asn, description)
                if errors >= max_consecutive_errors:
                    time.sleep(int(config.get('sleep_timers','short')))
                    errors = 0
            else:
                errors = 0
                self.__update_db_ris(description, entry)
                to_return = True
            syslog.syslog(syslog.LOG_DEBUG, 'RIS Whois to fetch: ' + str(self.global_db.scard(key_no_asn)))
            description = self.global_db.pop(key_no_asn)
        return to_return
