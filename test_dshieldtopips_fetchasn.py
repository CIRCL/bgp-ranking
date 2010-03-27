# -*- coding: utf-8 -*-

from dshield_topips import Dshield_TopIPs
from dshield_daily import Dshield_Daily
from fetch_asns import Fetch_ASNs
from models import *

d = Dshield_TopIPs()
#d = Dshield_Daily()
d.update()

f = Fetch_ASNs()
f.fetch_asns()

asns = ASNs_descriptions.query.all()

for asn in asns:
    print(asn)
    for ip in asn.ips:
        print(ip)
