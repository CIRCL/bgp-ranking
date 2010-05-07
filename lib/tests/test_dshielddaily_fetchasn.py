# -*- coding: utf-8 -*-

from modules.dshield_daily import DshieldDaily
from utils.fetch_asns import FetchASNs
from utils.models import *
d = DshieldDaily()
d.update()

f = FetchASNs()
f.start()

asns = ASNsDescriptions.query.all()

#for asn in asns:
#    print(asn)
#    for ip in asn.ips:
#        print(ip)

