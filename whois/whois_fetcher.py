#!/usr/bin/python
# -*- coding: utf-8 -*-
# Original Idea :
# =>  http://code.google.com/p/pywhois/source/browse/trunk/pywhois/parser.py

import re
from model import *
from utils.ip_manip import *
from utils.models import *
from socket import *
import time

def get_server_by_name(server):
    to_return = Assignations.query.filter(Assignations.whois==server).first()
    return to_return

def get_server_by_query(query):
    assignations = Assignations.query.filter(Assignations.block!='').all()
    server = None
    for assignation in assignations:
        if ip_in_network(query, assignation.block):
            if not server:
                server = assignation
            else:
                if ip_in_network(assignation.block, server.block ):
                    server = assignation
    return server

class WhoisFetcher(object):
    """Class to the Whois entry of a particular IP.
    """
    regex_whois = {
        # This whois contains a Korean and an English version, we only save the english one. 
        'whois.nic.or.kr' :  '# ENGLISH\n(.*)'
        }
    regex_riswhois = {
        'whois.ripe.net' : '% Information related to*\n(.*)'
        }
        
    def connect(self):
        self.s.connect((self.server,self.port))
        self.s.setblocking(0)
        time.sleep(0.1)
        try: 
            self.s.recv(1024)
        except:
            # The server does not send any "ehlo message"
            pass
        self.s.setblocking(1)
    
    def fetch_whois(self, query, keepalive = False):
        pre_options = self.pre_options
        if keepalive:
            pre_options += self.keepalive_options
        self.s.send(pre_options + query + self.post_options +' \n')
        self.text = ''
        while self.text == '':
            self.text = self.s.recv(1024).rstrip()
        special_regex = self.regex_whois.get(self.server, None)
        if special_regex:
            self.text = re.findall(special_regex, self.text )
        if not keepalive:
            self.s.close()
        return self.text

    def __set_values(self,  assignation):
        self.server = assignation.whois
        self.pre_options = assignation.pre_options
        self.post_options = assignation.post_options
        self.keepalive_options = assignation.keepalive_options
        self.port = assignation.port

    def __init__(self, server):
        self.__set_values(server)
        self.s = socket(AF_INET, SOCK_STREAM)
    
    def __repr__(self):
        return self.text
