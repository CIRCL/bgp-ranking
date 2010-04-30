#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

from initscript_helper import *

service = "raw_fetching"

options = \
        {'dshield_topips' : 'datas/dshield/topips/ http://www.dshield.org/feeds/topips.txt', 
        'dshield_daily' : 'datas/dshield/daily/ http://www.dshield.org/feeds/daily_sources', 
        'zeus_ipblocklist' : 'datas/zeus/ipblocklist/ http://www.abuse.ch/zeustracker/blocklist.php?download=ipblocklist'}

print "Starting fetching..."
for name, option in options.iteritems():
    print name + " to start..."
    service_start(servicename = service, param = option)
