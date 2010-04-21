# -*- coding: utf-8 -*-

from models import *
from whois.model import *
from threaded_fetching import Thread_ASN, Thread_Whois
from whois.whois_fetcher import get_server_by_query
from whois.whois_parsers import *
from ip_manip import ip_in_network

import redis
import time

class FetchASNs():
    """
    Make an AS whois request and set an ASNsDescriptions to all IPsDescriptions
    wich do not already have one. 
    
      1. Selection of all IPsDescriptions which do not have asn
      2. Query to the Ris Server with an IP 
      3. If the ASN is not already in the table ASNs, it is inserted 
      4. The description (name of the AS, IP block) of the ASN is inserted 
         into ASNsDescriptions
      5. Searching in the list (see 1.) for all IPs which belong to the IP block 
         of the current AS and set their ASN to the current
    
    Some IP found in the raw data have no AS (the owner is gone, it is in a legacy 
    block such as 192.0.0.0/8...) We don't delete this IPs from the database because 
    they might be usefull to trace an AS but they should not be used in the ranking 
    
    Note: If the IP as no AS, it is setted to the default ASN: -1. 
    Note 2: If we found one or more IP withoud AS in a raw data, a new default 
            ASNsDescriptions is created.
    """
    risServer = unicode('riswhois.ripe.net')
    default_asn_desc = None
    redis_keys = ['ris', 'whois']
    

    def __init__(self):
        """
        Push all the new IPs in the memcached server
        """
        # get all the IPs_descriptions which don't have asn
        
        self.redis = redis.Redis(db=0)
        self.ips_descriptions = IPsDescriptions.query.filter(IPsDescriptions.asn==None).all()
        for ip_description in self.ips_descriptions:
            self.redis.push(self.redis_keys[0],  ip_description.ip.ip)
        self.asns_descriptions = []

    def start(self):
        self.__get_asns()
        self.__get_whois()
        r_session = RankingSession()
        r_session.commit()
        r_session.close()
        
    
    def __update_db_ris(self, current,  data):
        """ 
        Update the database with the RIS whois informations
        """
        ris_whois = Whois(data,  self.risServer)
        if not ris_whois.origin:
            if not self.default_asn_desc:
                self.default_asn_desc = \
                    ASNsDescriptions(owner=unicode("IP without AS, see doc to know why"), \
                    ips_block=unicode('0.0.0.0'), asn=ASNs.query.get(unicode(-1)))
            current.asn = self.default_asn_desc
        else: 
            current_asn = ASNs.query.get(unicode(ris_whois.origin))
            if not current_asn:
                current_asn = ASNs(asn=unicode(ris_whois.origin))
            if not ris_whois.description:
                ris_whois.description = "This ASN has no description"
            asn_desc = ASNsDescriptions(owner=ris_whois.description.decode("iso-8859-1"), \
                                         ips_block=unicode(ris_whois.route), asn=current_asn)
            self.redis.push(self.redis_keys[1], ris_whois.route)
            self.asns_descriptions.append(asn_desc)
            current.asn = asn_desc

    def __in_current_asns_descriptions(self,  ip_description):
        for description in self.asns_descriptions:
            if ip_in_network(ip_description.ip.ip,description.ips_block):
                ip_description.asn = description
                return True
        return False

    def __get_asns(self):
        """ 
        Main function, initialise the WhoisFetcher and connect to riswhois.ripe.net
        Make a new connexion for each list of ris_dict. 
        """
        descriptions = self.ips_descriptions
        loop = 0
        while loop < 10 and len(descriptions) > 0:
            deferred = []
            for description in descriptions:
                if not self.__in_current_asns_descriptions(description):
                    entry = self.redis.get(description.ip.ip)
                    if not entry:
                        deferred.append(description)
                    else:
                        self.__update_db_ris(description, entry)
            time.sleep(1)
            descriptions = deferred
            loop += 1
        print(descriptions)

    def __get_whois(self):
        """ 
        Make a new connexion for each list of whois_dict. 
        """
        descriptions = self.asns_descriptions
        loop = 0
        while len(descriptions) > 0:
            deferred = []
            for description in descriptions:
                entry = self.redis.get(description.ips_block)
                if not entry:
                    deferred.append(description)
                else:
                    description.whois_address = entry[0]
                    description.whois = entry[1]
            descriptions = deferred
            loop += 1
            time.sleep(1)
            print(len(descriptions))
