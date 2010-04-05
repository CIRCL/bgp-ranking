# -*- coding: utf-8 -*-

from .modules.dshield_topips import DshieldTopIPs
from .modules.dshield_daily import DshieldDaily
from .utils.fetch_asns import FetchASNs
from .utils.models import *

d = DshieldTopIPs()
#d = DshieldDaily()
d.update()

f = FetchASNs()
f.fetch_asns()

asns = ASNsDescriptions.query.all()

for asn in asns:
    print(asn)
    for ip in asn.ips:
        print(ip)

