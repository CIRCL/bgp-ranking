#!/usr/bin/python

"""
Launch a connector for a particular whois server. 
"""

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config_file = "/mnt/data/gits/bgp-ranking/etc/bgp-ranking.conf"
config.read(config_file)
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

from whois_client.connector import Connector

def usage():
    print "whois_fetching.py server.tld"
    exit (1)

if len(sys.argv) < 2:
    usage()

c = Connector(sys.argv[1])
c.launch()
