# -*- coding: utf-8 -*-

from modules.zeustracker_ipblocklist import ZeustrackerIpBlockList
from utils.fetch_asns import FetchASNs
from utils.models import *

d = ZeustrackerIpBlockList()

d.update()

f = FetchASNs()
f.start()

asns = ASNsDescriptions.query.all()

for asn in asns:
    print(asn)
    for ip in asn.ips:
        print(ip)

