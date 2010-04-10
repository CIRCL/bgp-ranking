# -*- coding: utf-8 -*-

from .utils.models import *
from .whois.whois_parsers import Whois
from .whois.whois_fetcher import *
from .utils.ip_manip import ip_in_network

from socket import *


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
  
    risServer = 'riswhois.ripe.net'
    arguments = '-k -M '
    whoisPort = 43
    default_asn_desc = None

    def fetch_asns(self):
        """ Fetch the ASNs
        """
        # get all the IPs_descriptions which don't have asn
        ips_descriptions = IPsDescriptions.query.filter(\
                           IPsDescriptions.asn==None).all()
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((self.risServer,self.whoisPort))
        s.recv(1024)
        while len(ips_descriptions) > 0:
            description = ips_descriptions.pop()
            s.send(self.arguments + description.ip.ip + ' \n')
            self.__update_db(description, ips_descriptions, s.recv(1024))
        s.close()
        ranking_session.commit()

    def __update_db(self, current, ips_descriptions, data):
        """ Update the database with the whois
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
            whois = WhoisFetcher(current.ip.ip)
            asn_desc.whois = whois.text
            asn_desc.whois_address = unicode(whois.server)
            self.__check_all_ips(asn_desc, ips_descriptions)

    def __check_all_ips(self, asn_desc, ips_descriptions):
        """ Check if the ips are in an ip block we already know
        """
        if ips_descriptions:
            it = 0
            while it < len(ips_descriptions):
                desc = ips_descriptions[it]
                if ip_in_network(desc.ip.ip,asn_desc.ips_block):
                    desc.asn = asn_desc
                    ips_descriptions.pop(it)
                else:
                    it = it+1
