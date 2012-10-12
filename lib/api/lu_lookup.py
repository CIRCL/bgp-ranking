#!/usr/bin/python

import fileinput
import socket
from pyfurl.furl import Furl
from cymru.ip2asn.dns import DNSClient as ip2asn
import sys
import json

import api

CC_list = ['LU']
api.h.prepare()

f = Furl()
client = ip2asn()

to_print = []

for line in fileinput.input():
    f.decode(line.strip())
    u = f.get()
    #print u
    # print u['host']
    if u['host'] is not None or u['host'] is not '':
        try:
            ip = socket.gethostbyname(u['host'])
        except:
            ip = "127.0.0.1"
            pass
        l = client.lookup(ip,qType='IP')
        cc = getattr(l,'cc')
        asn = getattr(l,'asn')
        if cc is not None:
            ranking_info = api.get_asn_informations(asn)
            temp = []
            for day, data in ranking_info['data'].iteritems():
                temp.append({day: data['total']})
            entry = [cc, asn, line.strip(), temp]
            to_print += entry
    print json.dumps(to_print, sort_keys=True, indent=4)
