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

OrgID = { 
    'pochandles' : '(?:TechHandle|AbuseHandle|NOCHandle|OrgTechHandle|OrgAbuseHandle|OrgNOCHandle|OrgAdminHandle):[ ]*(.*)'
}

NetHandle = {
    'orgid'     : 'OrgID:[ ]*(.*)', 
    'parent'    : 'Parent:[ ]*(.*)', 
    'pochandles' : '(?:TechHandle|AbuseHandle|NOCHandle|OrgTechHandle|OrgAbuseHandle|OrgNOCHandle|OrgAdminHandle):[ ]*(.*)', 
    'netrange'  : 'NetRange:[ ]*(.*) - (.*)'

}

V6NetHandle = {
    'orgid'     : 'OrgID:[ ]*(.*)', 
    'parent'    : 'Parent:[ ]*(.*)', 
    'pochandles' : '(?:TechHandle|AbuseHandle|NOCHandle|OrgTechHandle|OrgAbuseHandle|OrgNOCHandle|OrgAdminHandle):[ ]*(.*)', 
    'netrange'  : 'NetRange:[ ]*(.*) - (.*)'
}

ASHandle = {
    'pochandles' : '(?:TechHandle|AbuseHandle|NOCHandle|OrgTechHandle|OrgAbuseHandle|OrgNOCHandle|OrgAdminHandle):[ ]*(.*)', 
    'orgid':  'OrgID:[ ]*(.*)'
}

POCHandle = { }

class ARINWhois(AbstractWhoisParser):
    """
    This class return a dump of the Whois. 
    Til we have a real implementation of whois in python, 
    we will use this class to return all the informations
    """
    possible_regex = {
        '^OrgID:'       : OrgID, 
        '^NetHandle:'   : NetHandle, 
        '^V6NetHandle:' : V6NetHandle, 
        '^ASHandle:'    : ASHandle, 
        '^POCHandle:'   : POCHandle
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
