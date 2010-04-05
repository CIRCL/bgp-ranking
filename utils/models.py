# -*- coding: utf-8 -*-

import datetime 
import sys

from elixir import *

reload(sys)
sys.setdefaultencoding('utf-8')

metadata.bind = "sqlite:///ranking.sqlite"
metadata.bind.echo = True

INET6_ADDRSTRLEN = 46


class IPs(Entity):
    """ Table which contains the IPs 
    """
    ip = Field(Unicode(INET6_ADDRSTRLEN), primary_key=True)
    ip_descriptions = OneToMany('IPsDescriptions')
    
    def __repr__(self):
        return 'IP: "%s"' % (self.ip)


class IPsDescriptions(Entity):
    """ Table which contains a description of the IPs
    and a link to the ASNs Descriptions 
    """
    list_name = Field(UnicodeText, required=True)
    timestamp = Field(DateTime, default=datetime.datetime.now)
    list_date = Field(DateTime, required=True)
    ip = ManyToOne('IPs')
    asn = ManyToOne('ASNsDescriptions')
  
    def __repr__(self):
        if not self.asn:
            return '[%s] List: "%s" \t %s' % (self.list_date, self.list_name,\
self.ip)
        else:
            return '\t[%s] List: "%s" \t %s \t %s' % (self.list_date,\
self.list_name, self.ip, self.asn.asn)
  
    
class ASNs(Entity):
    """ Table which contains the ASNs 
    """
    asn = Field(Integer, primary_key=True)
    asn_description = OneToMany('ASNsDescriptions')
  
    def __repr__(self):
        return 'ASN: "%s"' % (self.asn)
  

class ASNsDescriptions(Entity):
    """ Table which contains a description of the ASNs
    and a link to the IPs Descriptions 
    """
    timestamp = Field(DateTime, default=datetime.datetime.now)
    owner = Field(UnicodeText, required=True)
    ips_block = Field(Unicode(INET6_ADDRSTRLEN), required=True)
    asn = ManyToOne('ASNs')
    ips = OneToMany('IPsDescriptions')
  
    def __repr__(self):
        return '[%s] %s \t Owner: "%s" \t Block: "%s"' % (self.timestamp,\
self.asn, self.owner, self.ips_block)
  

setup_all()
create_all()


# Creation of the "default AS", see fetch_asn.py for more informations 
if not ASNs.query.get(str(-1)):
    ASNs(asn=str(-1))
    session.commit()

