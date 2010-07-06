#!/usr/bin/python
# -*- coding: utf-8 -*-
# Original Idea :
# =>  http://code.google.com/p/pywhois/source/browse/trunk/pywhois/parser.py

import re
from helpers.ip_manip import ip_in_network
from socket import *

class AbstractParser(object):
    """Abstract Class for parsing a Whois entry.
    """
    def __init__(self, text, server):
        self.text = text
        self.server = server
        self._whois_regs = self.possible_regex.get(self.server, {})

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
                    setattr(self, attr, value[0])
                return getattr(self, attr)
            else:
                raise KeyError("Unknown attribute: %s" % attr)
    
    def __repr__(self):
        return self.text
