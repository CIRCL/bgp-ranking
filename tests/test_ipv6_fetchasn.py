# -*- coding: utf-8 -*-

from modules.ipv6_test import IPv6_Test
from utils.fetch_asns import Fetch_ASNs
from utils.models import *

d = IPv6_Test()

d.update()

f = Fetch_ASNs()
f.fetch_asns()

asns = ASNs_descriptions.query.all()

for asn in asns:
    print(asn)
    for ip in asn.ips:
        print(ip)

