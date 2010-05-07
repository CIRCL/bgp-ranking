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

from helpers.initscript import *
import signal

"""
Start a process for all the modules listed in 'options'
"""

service = os.path.join(services_dir, "parse_raw_files")

options = \
    ['DshieldTopIPs', 
#    'DshieldDaily', 
    'ZeustrackerIpBlockList', 
    'ShadowserverSinkhole',  
    'ShadowserverReport',  
    'ShadowserverReport2',
    'Atlas'
    ]


for option in options:
    print option+" to start..."
    service_start(servicename = service, param = option)
