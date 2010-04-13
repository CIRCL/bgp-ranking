# -*- coding: utf-8 -*-
from model import *

import IPy

whois_metadata.drop_all()
whois_metadata.create_all()

# 'address' : option(s)
whois_pre_options = {
    'whois.ripe.net' :  unicode('-B '), 
    'riswhois.ripe.net' :  unicode('-M ')
    }

whois_keepalive_options = {
    'whois.ripe.net' :  unicode('-k '), 
    'riswhois.ripe.net' :  unicode('-k ')
    }
    
whois_post_options = {
    'whois.nic.ad.jp' :  unicode(' /e ')
    }

def check_network_validity(ip):
    return str(IPy.IP(ip))

def insert(assignations): 
    for ip,url in assignations:
        if url not in [ 'UNALLOCATED',  '6to4',  'teredo' ] \
                and not re.findall('\.',url):
            url = 'whois.' + url + '.net'
        # Buggy networks
        if ip == '210.71.128.0/16':
            ip = '210.71.128.0/17'
        if ip == '210.241.0.0/15':
            ip = '210.241.0.0/16'
        if ip == '221.138.0.0/13':
            ip = '221.138.0.0/15'
        Assignations(block=unicode(check_network_validity(ip)), whois=unicode(url))

def set_options():
    assignations = Assignations.query.all()
    for assignation in assignations: 
        url = assignation.whois
        assignation.pre_options = whois_pre_options.get(url,  '')
        assignation.post_options = whois_post_options.get(url,  '')
        assignation.keepalive_options = whois_keepalive_options.get(url,  '')

regex_ipv4 = '([^#][\d./]*)'
regex_ipv6 = '([^#][\d\w:/]*)'
regex_dns  = '([^#][\d\w.]*)'

f = open('whois/ip_del_list').read()
assignations = re.findall('[\n]*' + regex_ipv4 + '\t' + regex_dns + '\s*',f)
insert(assignations)

f = open('whois/ip6_del_list').read()
assignations = re.findall('[\n]*' + regex_ipv6 + '\t' + regex_dns + '\s*',f)
insert(assignations)

# Self defined servers
# to do the RIS Requests
Assignations(whois=unicode('riswhois.ripe.net'))

set_options()

whois_session.commit()


