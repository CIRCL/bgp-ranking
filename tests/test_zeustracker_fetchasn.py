# -*- coding: utf-8 -*-

from modules.zeustracker_ipblocklist import Zeustracker_IpBlockList
from utils.fetch_asns import Fetch_ASNs
from utils.models import *

d = Zeustracker_IpBlockList()

d.update()

f = Fetch_ASNs()
f.fetch_asns()

asns = ASNs_descriptions.query.all()

for asn in asns:
    print(asn)
    for ip in asn.ips:
        print(ip)

