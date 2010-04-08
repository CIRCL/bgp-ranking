#!/usr/bin/python
# -*- coding: utf-8 -*-
# Original Idea :
# =>  http://code.google.com/p/pywhois/source/browse/trunk/pywhois/parser.py

from whois import AbstractWhois

class RIS(AbstractWhois):
    """Class for parsing a RIS-Whois entry.
    """
    
    _whois_regs = {
        'route':       'route[6]?:[ ]*([^\n]*)',
        'origin':      'origin:[ ]*AS([^\n]*)',
        'description': 'descr:[ ]*([^\n]*)'
    }

class Whois(AbstractWhois):
    """
    This class return a dump of the Whois. 
    Til we have a real implementation of whois in python, 
    we will use this class to save all the informations
    """
    _whois_regs = {
        'dump':       '(.*)'
    }
