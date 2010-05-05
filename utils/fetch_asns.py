# -*- coding: utf-8 -*-

from models import *
from whois.model import *
from threaded_fetching import Thread_ASN, Thread_Whois
from whois.whois_fetcher import get_server_by_query
from whois.whois_parsers import *
from ip_manip import ip_in_network

import redis
import time

# Query keys 
redis_keys = ['ris', 'whois']
# Temporary redis database, used to push ris and whois requests
temp_reris_db = 0
# Cache redis database, used to set ris and whois responses
cache_reris_db = 1
# Sleep before fetch the deferred queries
sleep_timer = 1

class FetchASNs():
    """
    Abstract : Set an ASNsDescriptions to all IPsDescriptions wich do not already have one.
    
    This class is a little bit complicated, take a look in 
        doc/uml-diagramms/{Whois\ Fetching.png,RIS\ Fetching.png} 
    for more informations
    
    1. Initialize self.ips_descriptions with all descriptions without ASNsDescriptions
    2. Push all ips into redit
    3. For each ip_description: 
        a. check if the IP is not in a block we have already fetched
            - set the asn description 
        b. attempt to get the asn whois from redit
            - create the new asn description
            - append the asn description to self.asns_descriptions
        c. append the ip_description to the deferred list 
    4. For each asn_description
        a. attempt to get the asn whois from redit add it to the asn_description
        b. append the ip_description to the deferred list 
    
    Some IP found in the raw data have no AS (the owner is gone, it is in a legacy 
    block such as 192.0.0.0/8...) We don't delete this IPs from the database because 
    they might be usefull to trace an AS but they should not be used in the ranking 
    
    Note: If the IP as no AS, it is setted to the default ASN: -1. 
    Note 2: If we found one or more IP withoud AS in a raw data, a new default 
            ASNsDescriptions is created.
    """
    default_asn_desc = None
    

    def __init__(self):
        """
        Initialize the two connectors to the redis server 
        """        
        self.cache_db = redis.Redis(db=cache_reris_db)
        self.temp_db = redis.Redis(db=temp_reris_db)

    def __commit(self):
        """
        Commit the pending modifications in the database 
        """
        r_session = RankingSession()
        r_session.commit()
        r_session.close()
    
    def __update_db_ris(self, current,  data):
        """ 
        Update the database with the RIS whois informations
        Push the routes into redis (the whois queries will be done with it)
        """
        splitted = data.partition('\n')
        ris_origin = splitted[0]
        riswhois = splitted[2]
        ris_whois = Whois(riswhois,  ris_origin)
        if not ris_whois.origin:
            if not self.default_asn_desc:
                self.default_asn_desc = \
                    ASNsDescriptions(owner=unicode("IP without AS, see doc to know why"), \
                    ips_block=unicode('0.0.0.0'), asn=ASNs.query.get(unicode(-1)),  \
                    whois=unicode('None'), whois_address=unicode('None'), \
                    riswhois_origin=unicode('None') )
            current.asn = self.default_asn_desc
        else: 
            current_asn = ASNs.query.get(unicode(ris_whois.origin))
            if not current_asn:
                current_asn = ASNs(asn=unicode(ris_whois.origin))
            if not ris_whois.description:
                ris_whois.description = "This ASN has no description"
            asn_desc = ASNsDescriptions.query.filter_by(asn=current_asn, ips_block=unicode(ris_whois.route),\
                                                        owner=ris_whois.description.decode("iso-8859-1"),\
                                                        riswhois_origin=unicode(ris_origin)).first()
            if not asn_desc:
                asn_desc = ASNsDescriptions(asn=current_asn, ips_block=unicode(ris_whois.route), \
                                            owner=ris_whois.description.decode("iso-8859-1"), \
                                            riswhois_origin=unicode(ris_origin))
            self.temp_db.push(redis_keys[1], ris_whois.route)
            current.asn = asn_desc


    def get_asns(self, limit_first, limit_last):
        """ 
        Push the IP addresses of the IPsDescriptions without asn into redis and loop until all 
        the RIS Whois descriptions are found in the cache database of redis
        """
        self.ips_descriptions = IPsDescriptions.query.filter(IPsDescriptions.asn==None)[limit_first:limit_last]
        for ip_description in self.ips_descriptions:
            self.temp_db.push(redis_keys[0],  ip_description.ip.ip)
        while len(self.ips_descriptions) > 0:
            deferred = []
            for description in self.ips_descriptions:
                entry = self.cache_db.get(description.ip.ip)
                if not entry:
                    deferred.append(description)
                else:
                    self.__update_db_ris(description, entry)
            self.ips_descriptions = deferred
            time.sleep(sleep_timer)
            print('IP Desc: ' + str(len(self.ips_descriptions)))
        self.__commit()


    def get_whois(self, limit_first, limit_last):
        """ 
        Loop until all the Whois entry of the ASNsDescriptions (without whois entry...)
        are found in the cache database of redis
        """
        asns_descriptions = ASNsDescriptions.query.filter(ASNsDescriptions.whois==None)[limit_first:limit_last]
        while len(asns_descriptions) > 0:
            deferred = []
            for description in asns_descriptions:
                #FIXME: use sets and redis tags => http://simonwillison.net/static/2010/redis-tutorial/
                entry = self.cache_db.get(description.ips_block)
                if not entry:
                    deferred.append(description)
                else:
                    splitted = entry.partition('\n')
                    description.whois_address = splitted[0]
                    description.whois = splitted[2]
            asns_descriptions = deferred
            time.sleep(sleep_timer)
            print('Descriptions to fetch: ' + str(len(asns_descriptions)))
        self.__commit()
