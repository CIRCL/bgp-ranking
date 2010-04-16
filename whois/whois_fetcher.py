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
from elixir import *


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
    
    # Some funny whois implementations.... 
    regex_whois = {
        # This whois contains a Korean and an English version, we only save the english one. 
        'whois.nic.or.kr' :  '# ENGLISH\n(.*)'
        }
    regex_riswhois = {
        'whois.ripe.net' : '% Information related to*\n(.*)'
        }
    has_welcome_message = ['riswhois.ripe.net',  'whois.apnic.net',  'whois.ripe.net', 'whois.afrinic.net']
    has_info_message = ['whois.afrinic.net',  'whois.lacnic.net']
    need_an_ip = ['whois.arin.net']
    
    #FIXME: whois.arin.net refuse CIRD queries... we have to send an IP......
    
    def connect(self):
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.connect((self.server,self.port))
        if self.server in self.has_welcome_message:
            self.s.recv(1024)
        
    
    def fetch_whois(self, query, keepalive = False):
        pre_options = self.pre_options
        if keepalive:
            pre_options += self.keepalive_options
        if self.server in self.need_an_ip:
            query = first_ip(query)
        self.s.send(pre_options + query + self.post_options +' \n')
        if self.server in self.has_info_message:
            self.s.recv(1024)
        self.text = ''
        while self.text == '':
            self.text = self.s.recv(1024).rstrip()
        print(self.text)
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
    
    def __repr__(self):
        return self.text
