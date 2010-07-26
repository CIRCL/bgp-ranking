#!/usr/bin/python
# -*- coding: utf-8 -*-
# Original Idea :
# =>  http://code.google.com/p/pywhois/source/browse/trunk/pywhois/parser.py


#if __name__ == "__main__":
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
import sys
import os
sys.path.append(os.path.join(config.get('directories','root'),config.get('directories','libraries')))

from socket import *

import IPy
import re
import time
from elixir import *
import redis

import errno
import syslog
syslog.openlog('BGP_Ranking_Fetchers', syslog.LOG_PID, syslog.LOG_USER)

def get_all_servers_urls():
    """
    Get the URLs of all the whois servers 
    """
    return  redis.Redis(db=config.get('redis','whois_assignations')).smembers(config.get('assignations','servers_key'))


def get_server_by_query(query, r):
    to_return = None
    ranges = None
    key = str(query)
    ip = IPy.IP(query)
    if ip.version() == 4:
        regex = '.*[.]'
    else:
        regex = '.*[:]'
    while not ranges:
        key = re.findall(regex, key)
        if len(key) != 0:
           key = key[0][:-1]
        else:
            break
        ranges = r.smembers(key)
    best_range = None
    for range in ranges:
        network = IPy.IP(range)
        if ip in network:
            if best_range is not None:
                if network in best_range:
                    best_range = network
            else:
                best_range = network
    if best_range is not None:
        to_return = r.get(str(best_range))
    return to_return

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
    # Doesn't support CIDR queries -> we always do queries with ips 
#    need_an_ip = ['whois.arin.net', 'whois.nic.or.kr']
    
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
        self.s.send(pre_options + query + self.post_options +' \n')
        if self.server in self.has_info_message:
            self.s.recv(2048)
        self.text = ''
        loop = 0
        fs = self.s.makefile()
        prec = ''
        while 1:
            temp = fs.readline()
#            syslog.syslog(syslog.LOG_DEBUG, self.server + ": " + temp)
            if not temp or len(temp) == 0 or prec == temp == '\n':
                break
            self.text += temp 
            prec = temp 
        if len(self.text) == 0:
            syslog.syslog(syslog.LOG_ERR, "error (no response) with query: " + query + " on server " + self.server)
        else:
            part = self.whois_part.get(self.server, None)
            if part:
                self.text = self.text.partition(part)[2]
        if not keepalive:
            self.s.close()
        return self.text

    def __set_values(self,  server):
        """
        Set the needed informations concerning the server we want to use
        """
        r = redis.Redis(db=config.get('redis','whois_assignations'))
        pre_option_suffix = config.get('assignations','pre_option_suffix')
        post_option_suffix = config.get('assignations','post_option_suffix')
        keepalive_option_suffix = config.get('assignations','keepalive_option_suffix')
        port_option_suffix = config.get('assignations','port_option_suffix')
        self.server = server
        self.pre_options = r.get(server + pre_option_suffix)
        if self.pre_options == None:
            self.pre_options = ''
        self.post_options = r.get(server + post_option_suffix)
        if self.post_options == None:
            self.post_options = ''
        self.keepalive_options = r.get(server + keepalive_option_suffix)
        if self.keepalive_options == None:
            self.keepalive_options = ''
        self.port = r.get(server + port_option_suffix)
        if self.port == None:
            self.port = config.get('assignations','default_whois_port')
        self.port = int(self.port)

    def __init__(self, server):
        self.__set_values(server)
    
    def __repr__(self):
        return self.text

if __name__ == "__main__":
    f = WhoisFetcher('whois.arin.net')
    f.connect()
    print(f.fetch_whois('127.0.0.1', True))
    print(f.fetch_whois('127.0.0.1', True))
    print(f.fetch_whois('127.0.0.1', False))
    f.disconnect()
    f = WhoisFetcher('whois.ripe.net')
    f.connect()
    print(f.fetch_whois('127.0.0.1', True))
    print(f.fetch_whois('127.0.0.1', True))
    print(f.fetch_whois('127.0.0.1', False))
    f.disconnect()
    f = WhoisFetcher('whois.lacnic.net')
    f.connect()
    print(f.fetch_whois('200.3.14.10', False))
    f.disconnect()
    
    f = WhoisFetcher('whois.apnic.net')
    f.connect()
    print(f.fetch_whois('116.66.203.208', False))
    f.disconnect()
    
    f = WhoisFetcher('riswhois.ripe.net')
    f.connect()
    print(f.fetch_whois('200.3.14.10', False))
    f.disconnect()
    
    print get_all_servers_urls()
    print get_server_by_query('200.3.14.10')
    print get_server_by_query('127.0.0.1')
  
    
    
