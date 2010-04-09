#!/usr/bin/python
# -*- coding: utf-8 -*-
# Original Idea :
# =>  http://code.google.com/p/pywhois/source/browse/trunk/pywhois/parser.py

import re
from model import *
from .utils.ip_manip import *
from socket import *

class WhoisFetcher(object):
    """Class to the Whois entry of a particular IP.
    """
    regex_whois = {
        # This whois contains a Korean and an English version, we only save the english one. 
        'whois.nic.or.kr' :  '# ENGLISH\n(.*)'
        }
    
    def __fetch_whois(self):
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((self.server,self.port))
        s.setblocking(0)
        try: 
            s.recv(1024)
        except:
            pass
        s.setblocking(1)
        s.send(self.pre_options + self.ip + self.post_options +' \n')
        self.text = ''
        while 1:
            temp = s.recv(1024)
            if len(temp) == 0:
                break
            self.text += temp
        special_regex = self.regex_whois.get(self.server, None)
        if special_regex:
            self.text = re.findall(special_regex, self.text )
        s.close()

    def __find_server(self):
        assignations = Assignations.query.all()
        possibilities = []
        for assignation in assignations:
            if ip_in_network(self.ip, assignation.block):
                possibilities.append(assignation)
        assignation = smallest_network(possibilities)
        self.server = assignation.whois
        self.pre_options = assignation.pre_options
        self.post_options = assignation.post_options
        self.port = assignation.port


    def __init__(self, ip):
        self.ip = ip
        self.__find_server()
        self.__fetch_whois()
    
    def __repr__(self):
        return self.text
