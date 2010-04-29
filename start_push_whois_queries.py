#!/usr/bin/python
# -*- coding: utf-8 -*-

from utils.fetch_asns import FetchASNs
from utils.models import *
f = FetchASNs()
f.start()

asns = ASNsDescriptions.query.all()
for asn in asns:
    print(asn)
    for ip in asn.ips:
        print(ip)
