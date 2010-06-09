#!/usr/bin/python
import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('global','root')
sys.path.append(os.path.join(root_dir,config.get('global','lib')))
raw_data = os.path.join(root_dir,config.get('global','raw_data'))
sleep_timer = int(config.get('global','sleep_timer_short'))

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=os.path.join(root_dir,config.get('global','log_parse_raw_files')))

from modules.zeustracker_ipblocklist import ZeustrackerIpBlockList
from modules.dshield_daily import DshieldDaily
from modules.dshield_topips import DshieldTopIPs
from modules.shadowserver_sinkhole import ShadowserverSinkhole
from modules.shadowserver_report import ShadowserverReport
from modules.shadowserver_report2 import ShadowserverReport2
from modules.atlas import Atlas

import time

"""
Parse the file of a module
"""

def usage():
    print "parse_raw_files.py name"
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

while 1:
    module = modules[sys.argv[1]](raw_data)
    if module.update():
        print('Done with ' + sys.argv[1])
        logging.info('Done with ' + sys.argv[1])
    else:
        print('No files to parse for ' + sys.argv[1])
        logging.info('No files to parse for ' + sys.argv[1])
    time.sleep(sleep_timer)
