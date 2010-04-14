# -*- coding: utf-8 -*-


from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.schema import ThreadLocalMetaData
from elixir import *


#ranking_engine = create_engine("sqlite:///ranking.sqlite")#, echo=True)
ranking_engine = create_engine('mysql://root@localhost/ranking')
ranking_session = scoped_session(sessionmaker(bind=ranking_engine))
ranking_metadata = ThreadLocalMetaData()

__metadata__ = ranking_metadata
__session__ = ranking_session

import datetime 

INET6_ADDRSTRLEN = 46

class IPs(Entity):
    """ 
    Table which contains the IPs 
    """
    ip = Field(Unicode(INET6_ADDRSTRLEN), primary_key=True)
    ip_descriptions = OneToMany('IPsDescriptions')
    
    def __repr__(self):
        return 'IP: "%s"' % (self.ip)


class IPsDescriptions(Entity):
    """ 
    Table which contains a description of the IPs
    and a link to the ASNs Descriptions 
    """
    list_name = Field(UnicodeText, required=True)
    timestamp = Field(DateTime(timezone=True), default=datetime.datetime.utcnow)
    list_date = Field(DateTime(timezone=True), required=True)
    times = Field(Integer, default=1)
    ip = ManyToOne('IPs')
    asn = ManyToOne('ASNsDescriptions')
  
    def __repr__(self):
        to_return = '[%s] List: "%s" \t %s present %d time(s)' % (self.list_date, self.list_name,\
                    self.ip,  self.times)
        if self.asn:
            to_return += '\t %s' % (self.asn.asn)
        return to_return

    
class ASNs(Entity):
    """ 
    Table which contains the ASNs 
    """
    asn = Field(Integer, primary_key=True)
    asn_description = OneToMany('ASNsDescriptions')
  
    def __repr__(self):
        return 'ASN: "%d"' % (self.asn)
  

class ASNsDescriptions(Entity):
    """ 
    Table which contains a description of the ASNs
    and a link to the IPs Descriptions 
    """
    timestamp = Field(DateTime(timezone=True), default=datetime.datetime.utcnow)
    owner = Field(UnicodeText, required=True)
    ips_block = Field(Unicode(INET6_ADDRSTRLEN), required=True)
    whois = Field(Binary)
    whois_address = Field(UnicodeText)
    asn = ManyToOne('ASNs')
    ips = OneToMany('IPsDescriptions')
  
    def __repr__(self):
        return '[%s] %s \t Owner: "%s" \t Block: "%s"' % (self.timestamp,\
                self.asn, self.owner, self.ips_block)
