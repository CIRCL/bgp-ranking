# -*- coding: utf-8 -*-

from modules.ipv6_test import IPv6Test
from utils.fetch_asns import FetchASNs
from utils.models import *

d = IPv6Test()

d.update()

f = FetchASNs()
f.fetch_asns()

asns = ASNsDescriptions.query.all()

for asn in asns:
    print(asn)
    for ip in asn.ips:
        print(ip)

