# -*- coding: utf-8 -*-

from .utils.models import *
from .utils.whois_parser import WhoisEntry
from .utils.ip_manip import ip_in_network

from socket import *


class FetchASNs():
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
        session.commit()

    def __update_db(self, current, ips_descriptions, data):
        """ Update the database with the whois
        """
        whois = WhoisEntry(data)
        if not whois.origin:
            if not self.default_asn_desc:
                self.default_asn_desc = \
                ASNsDescriptions(owner=str("IP without AS, see doc to know why"), \
                ips_block=str('0.0.0.0'), asn=ASNs.query.get(str(-1)))
            current.asn = self.default_asn_desc
                
        else: 
            current_asn = ASNs.query.get(str(whois.origin))
            if not current_asn:
                current_asn = ASNs(asn=str(whois.origin))
            if not whois.description:
                whois.description = "This ASN has no description"
            asn_desc = ASNsDescriptions(owner=whois.description.decode(\
                       "iso-8859-1"), ips_block=str(whois.route), asn=current_asn)
            current.asn = asn_desc
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
