#!/usr/bin/python

"""
Launch a fetcher of Whois entries on a particular range found in the database.
FIXME: It would be great to find a way to merge the fetching of RIS Whois and Whois entries
"""

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

from fetch_asns import FetchASNs

def usage():
    print "get_range_whois_queries.py first_entry last_entry"
    exit (1)

if len(sys.argv) < 2:
    usage()
    
args = sys.argv[1].split(' ')

f = FetchASNs()
f.get_whois(int(args[0]), int(args[1]))

sys.exit(1)
