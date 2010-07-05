#!/usr/bin/python
import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

from fetch_asns import FetchASNs

"""
Get the ris entries from the redis server and put them into the database.
"""

def usage():
    print "get_range_ris_queries.py first_entry last_entry"
    exit (1)

if len(sys.argv) < 2:
    usage()
    
args = sys.argv[1].split(' ')

f = FetchASNs()
f.get_asns(int(args[0]), int(args[1]))

sys.exit(1)
