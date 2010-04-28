# -*- coding: utf-8 -*-

from modules.shadowserver_sinkhole import ShadowserverSinkhole
from modules.shadowserver_report import ShadowserverReport
from modules.shadowserver_report2 import ShadowserverReport2
from utils.fetch_asns import FetchASNs
from utils.models import *
d = ShadowserverSinkhole()
d.update()

f = FetchASNs()
f.start()

d = ShadowserverReport2()
d.update()

f = FetchASNs()
f.start()


d = ShadowserverReport()
d.update()

f = FetchASNs()
f.start()

asns = ASNsDescriptions.query.all()

for asn in asns:
    print(asn)
    for ip in asn.ips:
        print(ip)

