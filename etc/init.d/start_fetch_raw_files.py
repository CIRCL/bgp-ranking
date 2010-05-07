#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../bgp-ranking.conf")
root_dir = config.get('global','root')
sys.path.append(os.path.join(root_dir,config.get('global','lib')))
services_dir = os.path.join(root_dir,config.get('global','services'))
raw_data = os.path.join(root_dir,config.get('global','raw_data'))

from helpers.initscript import *

"""
Launch the raw fetching processes 
"""

service = os.path.join(services_dir, "fetch_raw_files")

options = \
        {'dshield_topips':  os.path.join(raw_data, 'dshield/topips/')  + ' http://www.dshield.org/feeds/topips.txt', 
        'dshield_daily':    os.path.join(raw_data, 'dshield/daily/')   + ' http://www.dshield.org/feeds/daily_sources', 
        'zeus_ipblocklist': os.path.join(raw_data, 'zeus/ipblocklist/')+ ' http://www.abuse.ch/zeustracker/blocklist.php?download=ipblocklist'}

print "Starting fetching..."
for name, option in options.iteritems():
    print name + " to start..."
    service_start(servicename = service, param = option)
