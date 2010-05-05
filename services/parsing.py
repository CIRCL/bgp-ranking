import sys

from modules.zeustracker_ipblocklist import ZeustrackerIpBlockList
from modules.dshield_daily import DshieldDaily
from modules.dshield_topips import DshieldTopIPs
from modules.shadowserver_sinkhole import ShadowserverSinkhole
from modules.shadowserver_report import ShadowserverReport
from modules.shadowserver_report2 import ShadowserverReport2
from modules.atlas import Atlas

"""
Parse the file of a module
"""

def usage():
    print "parsing.py name"
    exit (1)

if len(sys.argv) < 2:
    usage()

modules = \
    {'DshieldTopIPs' : DshieldTopIPs, 
    'DshieldDaily' : DshieldDaily, 
    'ZeustrackerIpBlockList' : ZeustrackerIpBlockList, 
    'ShadowserverSinkhole' : ShadowserverSinkhole,  
    'ShadowserverReport' : ShadowserverReport,  
    'ShadowserverReport2' : ShadowserverReport2, 
    'Atlas' : Atlas}

module = modules[sys.argv[1]]()
module.update()

print('Done with ' + sys.argv[1])
