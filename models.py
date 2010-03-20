# -*- coding: utf-8 -*-
from elixir import *
import datetime 

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

metadata.bind = "sqlite:///ranking.sqlite"
metadata.bind.echo = True

INET6_ADDRSTRLEN = 46

class IPs(Entity):
  """ Table which contains the IPs 
  """
  ip = Field(Unicode(INET6_ADDRSTRLEN), primary_key=True)
  ip_descriptions = OneToMany('IPs_descriptions')
    
  def __repr__(self):
    return 'IP: "%s"' % (self.ip)



class IPs_descriptions(Entity):
  """ Table which contains a description of the IPs and a link to the ASNs Descriptions 
  """
  list_name = Field(UnicodeText, required=True)
  timestamp = Field(DateTime, default=datetime.datetime.now)
  list_date = Field(DateTime, required=True)
  ip = ManyToOne('IPs')
  asn = ManyToOne('ASNs_descriptions')
  
  def __repr__(self):
    if not self.asn:
      return '[%s] List: "%s" \t %s' % (self.list_date, self.list_name, self.ip)
    else:
      return '[%s] List: "%s" \t %s \t %s' % (self.list_date, self.list_name, self.ip, self.asn.asn)
  
  
  
class ASNs(Entity):
  """ Table which contains the ASNs 
  """
  asn = Field(Integer, primary_key=True)
  asn_description = OneToMany('ASNs_descriptions')
  
  def __repr__(self):
    return 'ASN: "%s"' % (self.asn)
  
class ASNs_descriptions(Entity):
  """ Table which contains a description of the ASNs and a link to the IPs Descriptions 
  """
  timestamp = Field(DateTime, default=datetime.datetime.now)
  owner = Field(UnicodeText, required=True)
  ips_block = Field(Unicode(INET6_ADDRSTRLEN), required=True)
  asn = ManyToOne('ASNs')
  ips = OneToMany('IPs_descriptions')
  
  def __repr__(self):
    return '[%s] %s \t Owner: "%s" ' % (self.timestamp,  self.asn, self.owner)
  

setup_all()
create_all()