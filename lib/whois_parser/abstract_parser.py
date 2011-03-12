#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    AbstractParser
    ~~~~~~~~~~~~~~
    
    Abstract class for all sorts of "block parsers"
    
    .. note::
        Original Idea : http://code.google.com/p/pywhois/source/browse/trunk/pywhois/parser.py
"""

import re
from socket import *

class AbstractParser(object):
    """
        Abstract Class for parsing a Whois entry.
    
        You have to define in the subclass an attribute called possible_regex. 
        This attribute is a dictionary having this format: 
        
            ..
                
                \{
                    whois_server_1 \: dict_of_entries1,
                    
                    whois_server_2 \: dict_of_entries2,
                    
                \}

        The dict_of_entries will have this format:
        
            ..
                
                \{
                    key1 \: regex_matching_the information we need ,
                    
                    key2 \: regex_matching_the information we need ,
                    
                \}

        To use this abstract class, you have to initialise the subclass with 
        the text to parse and the name of the server used. The name ps yhe server is used to 
        pick the right dict_of_entries. 
    """
    
    def __init__(self, text, server):
        self.text = text
        self.server = server
        self._whois_regs = self.possible_regex.get(self.server, {})

    def __getattr__(self, attr):
        """
            he first time an attribute is called it will be generated in this function.
            The attribute is then set to be accessed directly by subsequent calls.
        """
        try: 
            # ensure that the attribute does not already exist
            return getattr(self.__class__, attr)
        except AttributeError:
            # try to generate a new attribute using the dict 
            whois_reg = self._whois_regs.get(attr)
            if whois_reg:
                # find the text matched by the regex 
                value = re.findall(whois_reg, self.text)
                if not value:
                    # set it to None if it does not match anything
                    setattr(self, attr, None)
                else:
                    # get the value and initialize a new attribute 
                    setattr(self, attr, value[0])
                return getattr(self, attr)
            else:
                raise KeyError("Unknown attribute: %s" % attr)
    
    def __repr__(self):
        return self.text
