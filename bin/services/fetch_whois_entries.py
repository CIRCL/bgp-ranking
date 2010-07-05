#!/usr/bin/python

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

from whois_client.connector import Connector

"""
A connector on a specific url
"""

def usage():
    print "whois_fetching.py server.tld"
    exit (1)

if len(sys.argv) < 2:
    usage()

c = Connector(sys.argv[1])
c.launch()
