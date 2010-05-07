#!/usr/bin/python
# -*- coding: utf-8 -*-
# Original Idea :
# =>  http://code.google.com/p/pywhois/source/browse/trunk/pywhois/parser.py

from abstract_whois import AbstractWhoisParser


"""Regex of the RIS-Whois entry.
"""
RIS = {
    'route':       'route[6]?:[ ]*([^\n]*)',
    'origin':      'origin:[ ]*AS([^\n]*)',
    'description': 'descr:[ ]*([^\n]*)'
}

RIPE = {
    'inetnum':  'inetnum:[ ]*([^\n]*)', 
    'netname':  'netname:[ ]*([^\n]*)', 
    'descr':    'descr:[ ]*([^\n]*)', 
    'country':  'country:[ ]*([^\n]*)'
}

Afrinic = {
    'netname':  'netname:[ ]*([^\n]*)'
}
    

class Whois(AbstractWhoisParser):
    """
    This class return a dump of the Whois. 
    Til we have a real implementation of whois in python, 
    we will use this class to return all the informations
    """
    possible_regex = {
        'riswhois.ripe.net' : RIS, 
        'whois.ripe.net'    : RIPE, 
        'whois.afrinic.net' : Afrinic
        }
