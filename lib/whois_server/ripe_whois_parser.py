#!/usr/bin/python
# -*- coding: utf-8 -*-
# Original Idea :
# =>  http://code.google.com/p/pywhois/source/browse/trunk/pywhois/parser.py


import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('global','root')
sys.path.append(os.path.join(root_dir,config.get('global','lib')))

from whois_parser.abstract_whois import AbstractWhoisParser

import re

inetnum = { }
domain = { }
inet6num = { }
aut_num = { }
route = { }
route6 = { }
as_block = { }
as_set = { }
rtr_set = { }
route_set = { }
org = { }
poetic_form = { }
poem = { }
peering_set = { }
limerick = { }
key_cert = { }
inet_rtr = { }
filter_set= { }

class RIPEWhois(AbstractWhoisParser):
    """
    This class return a dump of the Whois. 
    Til we have a real implementation of whois in python, 
    we will use this class to return all the informations
    """
    possible_regex = {
        '^inetnum:'    : inetnum,
        '^domain:'     : domain,
        '^inet6num:'   : inet6num,
        '^aut-num:'    : aut_num,
        '^route:'      : route,
        '^route6:'     : route6,
        '^as-block:'   : as_block,
        '^as-set:'     : as_set,
        '^rtr-set:'    : rtr_set,
        '^route-set:'  : route_set,
        '^org:'        : org,
        '^poetic-form:': poetic_form,
        '^poem:'       : poem,
        '^peering-set:': peering_set,
        '^limerick:'   : limerick,
        '^key-cert:'   : key_cert,
        '^inet-rtr:'   : inet_rtr,
        '^filter-set'  : filter_set
        }
    
    def __getattr__(self, attr):
        """The first time an attribute is called it will be calculated here.
        The attribute is then set to be accessed directly by subsequent calls.
        """
        try: 
            return getattr(self.__class__, attr)
        except AttributeError:
            whois_reg = self._whois_regs.get(attr)
            if whois_reg:
                value = re.findall(whois_reg, self.text)
                if not value:
                    setattr(self, attr, None)
                else:
                    setattr(self, attr, value)
                return getattr(self, attr)
            else:
                raise KeyError("Unknown attribute: %s" % attr)
