# -*- coding: utf-8 -*-
from elixir import *
import datetime 

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
  list_fetch_date = Field(DateTime, default=datetime.datetime.now)
  list_date = Field(DateTime)
  ip = ManyToOne('IPs')
  asn = ManyToOne('ASNs_descriptions')
  
  def __repr__(self):
    return 'List Name: "%s"' % (self.list_name)
  
  
  
class ASNs(Entity):
  """ Table which contains the ASNs 
  """
  asn = Field(Integer, primary_key=True)
  asn_description = OneToMany('ASNs_descriptions')
  
class ASNs_descriptions(Entity):
  """ Table which contains a description of the ASNs and a link to the IPs Descriptions 
  """
  seen = Field(DateTime, default=datetime.datetime.now)
  proprietary = (UnicodeText, required=True)
  ips_block = Field(Unicode(INET6_ADDRSTRLEN), required=True)
  asn = ManyToOne('ASNs')
  ips = OneToMany('IPs_descriptions')
  
  
  
  