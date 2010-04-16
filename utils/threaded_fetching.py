from whois.model import *
from models import *
from whois.whois_fetcher import *
from whois.whois_parsers import Whois

import errno
from threading import Thread

#__metadata__ = ThreadLocalMetaData()
#__metadata__.bind = whois_engine

#from sqlalchemy.orm import mapper as sqla_mapper
#
#def session_mapper(scoped_session):
#    def mapper(cls, *arg, **kw):
#        cls.query = scoped_session.query_property()
#        return sqla_mapper(cls, *arg, **kw)
#    return mapper


class Thread_ASN():
    risServer = unicode('riswhois.ripe.net')
    default_asn_desc = None

    def __init__ (self,ip_list):
        #Thread.__init__(self)
        self.ip_list = ip_list
        self.ranking_session = scoped_session(sessionmaker(bind=ranking_engine))
        self.asn_list = []

    def run(self):
        self.server = get_server_by_name(self.risServer)
        self.fetcher = WhoisFetcher(self.server)
        self.__fetch_asns_current_list()

    def __fetch_asns_current_list(self):
        """
        Fetch the ris whois for the list, using keepalive because we are on riswhois
        Disconnect when the whole list is done
        """
        broken_pipe = 0
        last = self.ip_list[len(self.ip_list) -1]
        self.fetcher.connect()
        for description in self.ip_list:
            try:
                whois = self.fetcher.fetch_whois(description.ip.ip,  True)
                if description == last:
                    whois = self.fetcher.fetch_whois(description.ip.ip)
                self.asn_list.append(self.__update_db(description,  whois))
            except IOError, e:
                if e.errno == errno.EPIPE and broken_pipe < 5:
                    self.ip_list.append(description)
                    broken_pipe += 1
                    self.fetcher.connect()
                else:
                    raise IOError(e)
                    
        self.ranking_session.commit()
        self.ranking_session.close()

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
            return asn_desc

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
                
    def setName(self,  name):
        self.name = name

class Thread_Whois():

    def __init__ (self, server, asn_list ):
        #Thread.__init__(self)
        self.server = server
        self.asn_list = asn_list
        self.ranking_session = scoped_session(sessionmaker(bind=ranking_engine))

    def run(self):
        self.__fetch_whois_current_list()
    
        
    def __fetch_whois_current_list(self):
        """
        Fetch the whois for the list, using keepalive if possible
        """
        fetch_server = get_server_by_name(self.server)
        keepalive_capable = (fetch_server.keepalive_options != '')
        whois_fetcher = WhoisFetcher(fetch_server)
        
        if keepalive_capable:
            whois_fetcher.connect()
            while len(self.asn_list) > 0:
                description = self.asn_list.pop()
                if len(self.asn_list) != 0:
                    whois = whois_fetcher.fetch_whois(description.ips_block,  True)
                else:
                    whois = whois_fetcher.fetch_whois(description.ips_block)
                description.whois = whois
                description.whois_address = self.server
        else:
            for description in self.asn_list:
                whois_fetcher.connect()
                whois = whois_fetcher.fetch_whois(description.ips_block)
                description.whois = whois
                description.whois_address = self.server
        self.ranking_session.commit()
        self.ranking_session.close()
    
