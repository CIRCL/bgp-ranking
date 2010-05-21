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

# Helpers
dict_contact_global = { 
        'mnt_by'    : 'mnt-by:[ ]*(.*)', # person
        'tech_c'    : 'tech-c:[ ]*(.*)', # person
        'admin_c'   : 'admin-c:[ ]*(.*)' # mntner
    }
dict_poem = { 
        'mnt_by'    : 'mnt-by:[ ]*(.*)', 
        'author'    : 'author:[ ]*(.*)', 
        'admin_c'   : 'admin-c:[ ]*(.*)' 
    }
routes = { 
        'mnt_by'    : 'mnt-by:[ ]*(.*)',        # mntner
        'origin'    : 'origin:[ ]*(.*)'         # aut-num
    }
# ------------------------

inetnum = { 'inetnum'  : 'inetnum:[ ]*(.*) - (.*)' }
inetnum.update(dict_contact_global)
    
domain = { 'zone_c'    : 'zone-c:[ ]*(.*)' }
domain.update(dict_contact_global)
    
inet6num = { 'inet6num'  : 'inet6num:[ ]*(.*)' }
inet6num.update(dict_contact_global)
    
aut_num = { 'org'       : 'org:[ ]*(.*)' }       # organisation
aut_num.update(dict_contact_global)

route = routes
    
route6 = { 
        'mnt_lower' : 'mnt-lower:[ ]*(.*)', # mntner
        'mnt_routes': 'mnt-routes:[ ]*(.*)' # mntner
    }
route6.update(routes)
    
as_block = { 
        'mnt_lower' : 'mnt-lower:[ ]*(.*)', 
        'org'       : 'org:[ ]*(.*)'        # organisation
    }
as_block.update(dict_contact_global)

as_set = { 'members'   : 'members:[ ]*(.*)' }
as_set.update(dict_contact_global)
    
rtr_set = dict_contact_global
    
route_set = dict_contact_global
    
poetic_form = dict_contact_global
    
poem = { 'form'      : 'form:[ ]*(.*)' }
poem.update(dict_poem)

peering_set = dict_contact_global
    
limerick = dict_poem
    
key_cert = { 'mnt_by'    : 'mnt-by:[ ]*(.*)' }
    
inet_rtr = {        
        'tech_c'    : 'tech-c:[ ]*(.*)', 
        'admin_c'   : 'admin-c:[ ]*(.*)', 
        'nic_hdl'   : 'nic-hdl:[ ]*(.*)',   # person
        'local_as'  : 'local-as:[ ]*(.*)'   # aut-num
    }
filter_set= dict_contact_global

irt = dict_contact_global
    
mntner = {
        'admin_c'       : 'admin-c:[ ]*(.*)', 
        'mnt_by'        : 'mnt-by:[ ]*(.*)', 
        'referral_by'   : 'referral-by:[ ]*(.*)'    # mntner
    }
    
organisation = {
        'mnt_ref'       : 'mnt-ref:[ ]*(.*)',       # mntner
        'mnt_by'        : 'mnt-by:[ ]*(.*)'
    }
    
person = {}

role = {        
        'tech_c'    : 'tech-c:[ ]*(.*)', 
        'admin_c'   : 'admin-c:[ ]*(.*)', 
        'nic_hdl'   : 'nic-hdl:[ ]*(.*)'
    }

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
        '^poetic-form:': poetic_form,
        '^poem:'       : poem,
        '^peering-set:': peering_set,
        '^limerick:'   : limerick,
        '^key-cert:'   : key_cert,
        '^inet-rtr:'   : inet_rtr,
        '^filter-set:'  : filter_set, 
        #Dummy
        '^irt:'         : irt , 
        '^mntner:'      : mntner , 
        '^organisation:': organisation , 
        '^person:'      : person ,  
        '^role:'        : role 
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
