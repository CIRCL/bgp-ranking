# -*- coding: utf-8 -*-

# TODO: implement keepalive if possible (-k with ripe.net)
# TODO: fetch asn from whois.ripe.net & other servers if possible 

from models import *
from whois.model import *
from threaded_fetching import Thread_ASN, Thread_Whois
from whois.whois_fetcher import get_server_by_query

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

    def __init__(self):
        """
        Initialisation of the dictionary to classify the IPs by whois server
        ris_dict = {'server.tld': [IP_Desc1, IP_Desc2...]}
        """
        # get all the IPs_descriptions which don't have asn
        ips_descriptions = IPsDescriptions.query.filter(IPsDescriptions.asn==None).all()
        self.ris_dict = {}
        for ip_description in ips_descriptions:
            server = get_server_by_query(ip_description.ip.ip)
            if not self.ris_dict.get(server.whois,  None):
               self.ris_dict[server.whois] = [ip_description]
            else:
                self.ris_dict[server.whois].append(ip_description)

    def fetch_asns(self):
        """ 
        Main function, initialise the WhoisFetcher and connect to riswhois.ripe.net
        Make a new connexion for each list of ris_dict. 
        """
        self.whois_dict = {}
        threadList = []
        for current_server in self.ris_dict:
            current = Thread_ASN(self.ris_dict[current_server])
            current.setName(current_server)
            threadList.append(current)
            #current.start()
            current.run()
        for thread in threadList:
            #thread.join()
            self.whois_dict[thread.name] = thread.asn_list
        self.__fetch_whois()

    def __fetch_whois(self):
        """ 
        Make a new connexion for each list of whois_dict. 
        """
        for server in self.whois_dict:
            print(server)
            current = Thread_Whois(server, self.whois_dict[server])
            #current.start()
            current.run()
