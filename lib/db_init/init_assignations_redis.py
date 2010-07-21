#!/usr/bin/python
# -*- coding: utf-8 -*-

from make_ip_keys import *

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

import re
import IPy
import redis

# 'address' : option(s)
whois_pre_options = {
    #'whois.ripe.net' :  '-B ', 
    'riswhois.ripe.net' : '-M '
    }

whois_keepalive_options = {
    'whois.ripe.net' : '-k ', 
    'riswhois.ripe.net' : '-k '
    }
    
whois_post_options = {
    'whois.nic.ad.jp' : ' /e '
    }

whois_port_options = {
    config.get('whois_server', 'hostname') : config.get('whois_server', 'port')
    }
    
not_a_dns = [ 'UNALLOCATED',  '6to4',  'teredo' ]
derouted = ['6bone', 'v6nic']

to_drop = not_a_dns + derouted

def insert(assignations):
    maker = MakeIPKeys(IPy.IP(assignations[0][0]).version() == 4)
    for ip,url in assignations:
        if url not in to_drop :
            if not re.findall('\.',url):
                url = 'whois.' + url + '.net'
        # All the urls has to be pushed in the list: 
        # elsewhere there is no running process to put them out of redis...
        urls.add(url)
        # Buggy networks
        if ip == '210.71.128.0/16':
            ip = '210.71.128.0/17'
        if ip == '210.241.0.0/15':
            ip = '210.241.0.0/16'
        if ip == '221.138.0.0/13':
            ip = '221.138.0.0/15'
        net = IPy.IP(ip)
        first = net.net()
        last = net.broadcast()
        sets = maker.intermediate_sets(str(first), str(last))
        push_sets(sets, ip, url)

def push_sets(sets, ip, url):
    for set in sets:
        redis.sadd(set, ip)
        redis.set(ip, url)
#        redis.sadd(url, ip)

servers_key = config.get('assignations','servers_key')

def push_servers(urls):
    for url in urls:
        redis.sadd(servers_key, url)

pre_option_suffix = config.get('assignations','pre_option_suffix')
post_option_suffix = config.get('assignations','post_option_suffix')
keepalive_option_suffix = config.get('assignations','keepalive_option_suffix')
port_option_suffix = config.get('assignations','port_option_suffix')

def set_options():
    for url in urls:
        pre = whois_pre_options.get(url,  None)
        post = whois_post_options.get(url,  None)
        keepalive = whois_keepalive_options.get(url,  None)
        port = whois_port_options.get(url,  None)
        if pre:
            redis.set(url + pre_option_suffix, pre)
        if post:
            redis.set(url + post_option_suffix, post)
        if keepalive:
            redis.set(url + keepalive_option_suffix, keepalive)
        if port:
            redis.set(url + port_option_suffix, port)

redis = redis.Redis(db=config.get('redis','whois_assignations'))
urls = set()

regex_ipv4 = '([^#][\d./]*)'
regex_ipv6 = '([^#][\d\w:/]*)'
regex_dns  = '([^#][\d\w.]*)'

f = open('ip_del_list').read()
assignations = re.findall('[\n]*' + regex_ipv4 + '\t' + regex_dns + '\s*',f)
insert(assignations)

f = open('ip6_del_list').read()
assignations = re.findall('[\n]*' + regex_ipv6 + '\t' + regex_dns + '\s*',f)
insert(assignations)

# Self defined servers
# to do the RIS Requests
urls.add('riswhois.ripe.net')
# local queries -> http://gitorious.org/whois-server
urls.add(config.get('whois_server', 'hostname'))

set_options()
push_servers(urls)
