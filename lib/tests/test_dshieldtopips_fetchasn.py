# -*- coding: utf-8 -*-

from modules.dshield_topips import DshieldTopIPs
from utils.fetch_asns import FetchASNs
from utils.models import *
d = DshieldTopIPs()
d.update()

f = FetchASNs()
f.start()

asns = ASNsDescriptions.query.all()

for asn in asns:
    print(asn)
    for ip in asn.ips:
        print(ip)

