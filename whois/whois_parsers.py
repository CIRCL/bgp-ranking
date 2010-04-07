#!/usr/bin/python
# -*- coding: utf-8 -*-
# Original Idea :
# =>  http://code.google.com/p/pywhois/source/browse/trunk/pywhois/parser.py

from whois import *

class RIS(Whois):
    """Class for parsing a RIS-Whois entry.
    """
    _whois_regs = {
        'route':       'route[6]?:[ ]*([^\n]*)',
        'origin':      'origin:[ ]*AS([^\n]*)',
        'description': 'descr:[ ]*([^\n]*)'
    }

class RIPE(Whois):
    """Class for parsing a RIS-Whois entry.
    """
    _whois_regs = {
        'route':       'route[6]?:[ ]*([^\n]*)',
        'origin':      'origin:[ ]*AS([^\n]*)',
        'description': 'descr:[ ]*([^\n]*)'
    }

class APNIC(Whois):
    """Class for parsing a RIS-Whois entry.
    """
    _whois_regs = {
        'route':       'route[6]?:[ ]*([^\n]*)',
        'origin':      'origin:[ ]*AS([^\n]*)',
        'description': 'descr:[ ]*([^\n]*)'
    }
