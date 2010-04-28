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

import errno

def get_all_servers():
    to_return = set()
    servers = Assignations.query.all()
    for server in servers:
        if server.whois not in [ 'UNALLOCATED',  '6to4',  'teredo' ]:
            to_return.add(server.whois)
    return to_return

def get_server_by_name(server):
    """
    Return the entry of 'server' from the Assignation's database
    """
    to_return = Assignations.query.filter(Assignations.whois==server).first()
    return to_return

def get_server_by_query(query):
    """
    Return the server entry corresponing to 'query' from the Assignation's database
    Query is an IP address and is included in one of the block of the database. We have to find the 
    smallest to fetch the more accurate informations. 
    """
    assignations = Assignations.query.filter(Assignations.block!=unicode('')).all()
    while len(assignations) == 1:
        assignations = Assignations.query.filter(Assignations.block!=unicode('')).all()
    server = None
    for assignation in assignations:
        if ip_in_network(query, assignation.block):
            if not server:
                server = assignation
            else:
                if ip_in_network(assignation.block, server.block ):
                    server = assignation
    if not server:
        print(assignations)
    return server

class WhoisFetcher(object):
    """Class to the Whois entry of a particular IP.
    """
    
    # Some funny whois implementations.... 
    whois_part = {
        # This whois contains a Korean and an English version, we only need the english one, \
        # which comes after "ENGLISH\n"
        'whois.nic.or.kr' :  "ENGLISH\n"
        }
    # In case we want to get the RIS informations given by other servers than riswhois.ripe.net
    regex_riswhois = {
        'whois.ripe.net' : '% Information related to*\n(.*)'
        }
    # Message BEFORE the query 
    has_welcome_message = ['riswhois.ripe.net',  'whois.apnic.net',  'whois.ripe.net', 'whois.afrinic.net']
    # Message AFTER the query
    has_info_message = ['whois.ripe.net', 'whois.afrinic.net',  'whois.lacnic.net']
    # Doesn't support CIDR queries
    need_an_ip = ['whois.arin.net', 'whois.nic.or.kr']
    # The response is splitted....
    splitted = ['whois.nic.or.kr']
    
    s = socket(AF_INET, SOCK_STREAM)
    
    def connect(self):
        """
        TCP connection to one on the whois servers
        """
        self.s = socket(AF_INET, SOCK_STREAM)
        self.s.connect((self.server,self.port))
        if self.server in self.has_welcome_message:
            self.s.recv(1024)
        
    def disconnect(self):
        """
        Close the TCP connection 
        """
        self.s.close()
    
    def fetch_whois(self, query, keepalive = False):
        """
        Fetch the whois informations. Keep the connection alive if needed. 
        """
        pre_options = self.pre_options
        if keepalive:
            pre_options += self.keepalive_options
        if self.server in self.need_an_ip:
            query = first_ip(query)
        self.s.send(pre_options + query + self.post_options +' \n')
        if self.server in self.has_info_message:
            self.s.recv(2048)
        self.text = ''
        loop = 0
        while self.text == '' and loop < 5  :
            self.text = self.s.recv(4096).rstrip()
            loop += 1
            if self.text != '' and self.server in self.splitted:
                self.text += self.s.recv(4096).rstrip()
        if loop == 5:
            print("error (no response) with query: " + query + " on server " + self.server)
        part = self.whois_part.get(self.server, None)
        if part:
            self.text = self.text.partition(part)[2]
        if not keepalive:
            self.s.close()
        return self.text

    def __set_values(self,  assignation):
        """
        Set the needed informations concerning the server we want to use
        """
        self.server = assignation.whois
        self.pre_options = assignation.pre_options
        self.post_options = assignation.post_options
        self.keepalive_options = assignation.keepalive_options
        self.port = assignation.port

    def __init__(self, server):
        self.__set_values(server)
    
    def __repr__(self):
        return self.text
