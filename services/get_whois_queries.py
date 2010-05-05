import sys
from utils.fetch_asns import FetchASNs

"""
Get the whois queries from the redis server
"""

def usage():
    print "get_whois_queries.py first_entry last_entry"
    exit (1)

if len(sys.argv) < 2:
    usage()
    
args = sys.argv[1].split(' ')

f = FetchASNs()
f.get_whois(int(args[0]), int(args[1]))
