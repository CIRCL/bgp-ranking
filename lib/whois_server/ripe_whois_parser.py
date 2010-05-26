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

# Dict entries 
mnt_by      = { 'mnt_by'    : '\nmnt-by:[ ]*(.*)' }       # mntner
mnt_lower   = { 'mnt_lower' : '\nmnt-lower:[ ]*(.*)' }    # mntner
mnt_routes  = { 'mnt_routes': '\nmnt-routes:[ ]*(.*)' }   # mntner
mnt_ref     = { 'mnt_ref'   : '\nmnt-ref:[ ]*(.*)' }      # mntner

mnt_irt     = { 'mnt_irt'   : '\nmnt-irt:[ ]*(.*)' }      # irt

tech_c      = { 'tech_c'    : '\ntech-c:[ ]*(.*)' }       # person
admin_c     = { 'admin_c'   : '\nadmin-c:[ ]*(.*)' }      # person
author      = { 'author'    : '\nauthor:[ ]*(.*)' }       # person
zone_c      = { 'zone_c'    : '\nzone-c:[ ]*(.*)' }       # person
nic_hdl     = { 'nic_hdl'   : '\nnic-hdl:[ ]*(.*)' }      # person

origin      = { 'origin'    : '\norigin:[ ]*(.*)' }       # aut-num
members     = { 'members'   : '\nmembers:[ ]*(.*)' }      # aut-num
local_as    = { 'local_as'  : '\nlocal-as:[ ]*(.*)' }     # aut-num

# Sometimes, the second IP is on the next line....
inum        = { 'inetnum'   : '^inetnum:[ ]*(.*)[ ]*-[ ]*(.*)' , 'inetnum2l'   : '^inetnum:[ ]*(.*)[ \n]*-[ ]*(.*)'}
i6num       = { 'inet6num'  : '^inet6num:[ ]*(.*)' }

org         = { 'org'       : '\norg:[ ]*(.*)' }          # organisation
form        = { 'form'      : '\nform:[ ]*(.*)' }         # poetic-form

all_possible_keys = {}

all_possible_keys.update(mnt_by) 
all_possible_keys.update(mnt_lower)
all_possible_keys.update(mnt_routes) 
all_possible_keys.update(mnt_ref) 
all_possible_keys.update(mnt_irt) 

all_possible_keys.update(tech_c) 
all_possible_keys.update(admin_c) 
all_possible_keys.update(author)
all_possible_keys.update(zone_c)

all_possible_keys.update(inum)
all_possible_keys.update(i6num)

all_possible_keys.update(origin)
all_possible_keys.update(members)
all_possible_keys.update(local_as)
all_possible_keys.update(org)
all_possible_keys.update(form)

class RIPEWhois(AbstractWhoisParser):
    """
    This class return a dump of the Whois. 
    Til we have a real implementation of whois in python, 
    we will use this class to return all the informations
    """
#    possible_regex = {
#        '^inetnum:'    : inetnum,
#        '^domain:'     : domain,
#        '^inet6num:'   : inet6num,
#        '^aut-num:'    : aut_num,
#        '^route:'      : route,
#        '^route6:'     : route6,
#        '^as-block:'   : as_block,
#        '^as-set:'     : as_set,
#        '^rtr-set:'    : rtr_set,
#        '^route-set:'  : route_set,
#        '^poetic-form:': poetic_form,
#        '^poem:'       : poem,
#        '^peering-set:': peering_set,
#        '^limerick:'   : limerick,
#        '^key-cert:'   : key_cert,
#        '^inet-rtr:'   : inet_rtr,
#        '^filter-set:'  : filter_set, 
#        #Dummy
#        '^irt:'         : irt , 
#        '^mntner:'      : mntner , 
#        '^organisation:': organisation , 
#        '^person:'      : person ,  
#        '^role:'        : role 
#        }

    def __init__(self, text, server):
        self.text = text
        self.server = server
        self._whois_regs = all_possible_keys
    
    def __getattr__(self, attr):
        """The first time an attribute is called it will be calculated here.
        The attribute is then set to be accessed directly by subsequent calls.
        """
        to_return = getattr(self.__class__, attr, None)
        if to_return is None:
            whois_reg = self._whois_regs.get(attr, None)
            if whois_reg is not None:
                value = re.findall(whois_reg, self.text)
                if len(value) == 0 :
                    setattr(self, attr, None)
                else:
                    setattr(self, attr, value)
                to_return = getattr(self, attr)
            else:
                print("Unknown attribute: %s" % attr)
        return to_return


# Should not be used anymore
#inetnum = {}
#inetnum.update(inum, mnt_by, mnt_lower, mnt_routes, tech_c, admin_c)
#    
#domain = {}
#domain.update(zone_c, tech_c, admin_c, mnt_by)
#    
#inet6num = {}
#inet6num.update(i6num, tech_c, admin_c, mnt_by, mnt_lower, mnt_routes)
#    
#aut_num = {}
#aut_num.update(org, mnt_by, tech_c, admin_c, mnt_routes, mnt_lower)
#
#route = {}
#route.update(mnt_by, origin)
#    
#route6 = route
#route6.update(mnt_lower, mnt_routes)
#    
#as_block = {}
#as_block.update(tech_c, admin_c, mnt_by, mnt_lower, org)
#
#as_set = {}
#as_set.update(members, tech_c, admin_c, mnt_by)
#    
#rtr_set = {}
#rtr_set.update(tech_c, admin_c, mnt_by)
#    
#route_set = {}
#route_set.update(tech_c, admin_c, mnt_by)
#    
#poetic_form = {}
#poetic_form.update(tech_c, admin_c, mnt_by)
#    
#poem = {}
#poem.update(form, mnt_by, author, admin_c)
#
#peering_set = {}
#peering_set.update(tech_c, admin_c, mnt_by)
#    
#limerick = {}
#limerick.update(mnt_by, author, admin_c)
#    
#key_cert = mnt_by
#    
#inet_rtr = {}
#inet_rtr.update(tech_c, admin_c, nic_hdl, local_as)
#
#
#filter_set = {}
#filter_set.update(tech_c, admin_c, mnt_by)
#
#irt = {}
#irt.update(tech_c, admin_c, mnt_by)
#    
#mntner = {}
#mntner.update(admin_c, mnt_by, referral_by)
#    
#organisation = {}
#organisation.update(mnt_ref, mnt_by)
#    
#person = {}
#
#role = {}
#role.update(tech_c, admin_c, nic_hdl)
