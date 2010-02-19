# -*- coding: utf-8 -*-
from elixir import *
import datetime 

metadata.bind = "sqlite:///ranking.sqlite"
metadata.bind.echo = True

INET6_ADDRSTRLEN = 46

class IPs(Entity):
  ip = Field(Unicode(INET6_ADDRSTRLEN), primary_key=True)
  OneToMany('ips_description')
  ip_descriptions = OneToMany('IPs_descriptions')
    
  def __repr__(self):
    return 'IP: "%s"' % (self.ip)



class IPs_descriptions(Entity):
  list_name = Field(UnicodeText, required=True)
  list_fetch_date = Field(DateTime, default=datetime.datetime.now)
  list_date = Field(DateTime)
  ip = ManyToOne('IPs')
    
  def __repr__(self):
    return 'List Name: "%s"' % (self.list_name)
