# -*- coding: utf-8 -*-

from modules.dshield_topips import Dshield_TopIPs
from modules.dshield_daily import Dshield_Daily
from utils.fetch_asns import Fetch_ASNs
from utils.models import *

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

