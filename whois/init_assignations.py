# -*- coding: utf-8 -*-
from model import *

drop_all()
create_all()

# 'address' : [pre_options, post_options]
options = {
    'whois.nic.ad.jp' :  [unicode(''), unicode(' /e ')], 
    'whois.ripe.net' :  [unicode('-B '), unicode('')]
    }



def insert(assignations): 
    for ip,url in assignations:
        if url == 'UNALLOCATED' or url == '6to4' or url == 'teredo':
            Assignations(block=unicode(ip), whois=unicode(url))
        else: 
            if not re.findall('\.',url):
                url = 'whois.' + url + '.net'
            assignations = Assignations(block=unicode(ip), whois=unicode(url))
            whois_options = options.get(url,  None)
            if whois_options:
                assignations.pre_options = whois_options[0]
                assignations.post_options = whois_options[1]

regex_ipv4 = '([^#][\d./]*)'
regex_ipv6 = '([^#][\d\w:/]*)'
regex_dns  = '([^#][\d\w.]*)'

f = open('whois/ip_del_list').read()
assignations = re.findall('[\n]*' + regex_ipv4 + '\t' + regex_dns + '\s*',f)
insert(assignations)

f = open('whois/ip6_del_list').read()
assignations = re.findall('[\n]*' + regex_ipv6 + '\t' + regex_dns + '\s*',f)
insert(assignations)

whois_session.commit()


