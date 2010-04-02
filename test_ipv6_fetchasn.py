# -*- coding: utf-8 -*-

from ipv6_test import IPv6_Test
from fetch_asns import Fetch_ASNs
from models import *

d = IPv6_Test()

d.update()

f = Fetch_ASNs()
f.fetch_asns()

asns = ASNs_descriptions.query.all()

for asn in asns:
    print(asn)
    for ip in asn.ips:
        print(ip)

