# -*- coding: utf-8 -*-

# TODO: implement keepalive if possible (-k with ripe.net)
# TODO: fetch asn from whois.ripe.net & other servers if possible 

from models import *
from whois.model import *
from whois.whois_parsers import Whois
from whois.whois_fetcher import *
from ip_manip import ip_in_network

from threading import Thread

from socket import *
import errno



class Thread_ASN(Thread):
    risServer = unicode('riswhois.ripe.net')
    default_asn_desc = None

    def __init__ (self,ip_list ):
        Thread.__init__(self)
        self.ip_list = ip_list
        self.server = get_server_by_name(self.risServer)

    def run(self):
        self.fetcher = WhoisFetcher(self.server)
        self.__fetch_asns_current_list()

    def __fetch_asns_current_list(self):
        """
        Fetch the ris whois for the list, using keepalive because we are on riswhois
        Disconnect when the whole list is done
        """
        broken_pipe = 0
        last = self.ip_list[len(self.ip_list) -1]
        for description in self.ip_list:
            try:
                whois = self.fetcher.fetch_whois(description.ip.ip,  True)
                if description == last:
                    whois = self.fetcher.fetch_whois(description.ip.ip)
                self.__update_db(description,  whois)
            except IOError, e:
                if e.errno == errno.EPIPE and broken_pipe < 5:
                    self.ip_list.append(description)
                    broken_pipe += 1
                    self.fetcher.connect()
                else:
                    raise IOError(e)

    def __update_db(self, current, data):
        """ 
        Update the database with the RIS whois informations and initialize whois_dict
        in order to make the whois requests, by whois server. 
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
            asn_desc = ASNsDescriptions(owner=ris_whois.description.decode(\
                       "iso-8859-1"), ips_block=unicode(ris_whois.route), asn=current_asn)
            current.asn = asn_desc
            if not self.whois_dict.get(self.current_server,  None):
               self.whois_dict[self.current_server] = [asn_desc]
            else:
                self.whois_dict[self.current_server].append(asn_desc)
            self.__check_all_ips(asn_desc)

    def __check_all_ips(self, asn_desc):
        """ 
        Check if the ips are in an ip block we already know and drop them from the list 
        """
        it = 0
        while it < len(self.ip_list):
            desc = self.ip_list[it]
            if ip_in_network(desc.ip.ip,asn_desc.ips_block):
                desc.asn = asn_desc
                self.ip_list.pop(it)
            else:
                it = it+1

class Thread_Whois(Thread):

    def __init__ (self, server, asn_list ):
        Thread.__init__(self)
        self.server = server
        self.asn_list = asn_list

    def run(self):
        self.__fetch_whois_current_list()
    
        
    def __fetch_whois_current_list(self):
        """
        Fetch the whois for the list, using keepalive if possible
        """
        fetch_server = get_server_by_name(server)
        keepalive_capable = (fetch_server.keepalive_options != '')
        whois_fetcher = WhoisFetcher(fetch_server)
        
        if keepalive_capable:
            whois_fetcher.connect()
            while len(asn_list) > 0:
                description = asn_list.pop()
                if len(asn_list) != 0:
                    whois = whois_fetcher.fetch_whois(description.ips_block,  True)
                else:
                    whois = whois_fetcher.fetch_whois(description.ips_block)
                description.whois = whois
                description.whois_address = server
        else:
            for description in asn_list:
                whois_fetcher.connect()
                whois = whois_fetcher.fetch_whois(description.ips_block)
                description.whois = whois
                description.whois_address = server
        this.ranking_session.commit()
        this.ranking_session.close()
    

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
        self.whois_dict = {}

    def fetch_asns(self):
        """ 
        Main function, initialise the WhoisFetcher and connect to riswhois.ripe.net
        Make a new connexion for each list of ris_dict. 
        """
        for current_server in self.ris_dict:
            current = Thread_ASN(self.ris_dict[current_server])
            current.setName(current_server)
            current.start()
        self.__fetch_whois()

    def __fetch_whois(self):
        """ 
        Make a new connexion for each list of whois_dict. 
        """
        for server in self.whois_dict:
            current = Thread_Whois(server, self.whois_dict[server])
            current.start()
