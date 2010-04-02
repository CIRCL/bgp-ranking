# -*- coding: utf-8 -*-

from utils.models import *
from utils.whoisParser import WhoisEntry
from utils.ip_manip import ip_in_network

from socket import *


class Fetch_ASNs():
    risServer = 'riswhois.ripe.net'
    arguments = '-k -M '
    whoisPort = 43

    def fetch_asns(self):
        """ Fetch the ASNs
        """
        # get all the IPs_descriptions which don't have asn
        ips_descriptions = IPs_descriptions.query.filter(\
IPs_descriptions.asn==None).all()
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
            # FIXME: handle the error properly ! the ip has no AS! 
            
            pass
        else: 
            current_asn = ASNs.query.get(unicode(whois.origin))
            if not current_asn:
                current_asn = ASNs(asn=unicode(whois.origin))
            if not whois.description:
                whois.description = "This ASN has no description"
            asn_desc = ASNs_descriptions(owner=whois.description.decode(\
"iso-8859-1"), ips_block=unicode(whois.route), asn=current_asn)
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
