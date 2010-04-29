#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

import sys
import os
import signal
from initscript_helper import *


service = "parsing"
options = \
    ['DshieldTopIPs', 
#    'DshieldDaily', 
    'ZeustrackerIpBlockList', 
    'ShadowserverSinkhole',  
    'ShadowserverReport',  
    'ShadowserverReport2'
    ]


for option in options:
    print option+" to start..."
    service_start(servicename = service, param = option)
