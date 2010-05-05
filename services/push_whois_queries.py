import sys
from utils.fetch_asns import FetchASNs

"""
Push the whois queries into the redis server
"""

def usage():
    print "push_whois_queries.py first_entry last_entry"
    exit (1)

if len(sys.argv) < 2:
    usage()
    
args = sys.argv[1].split(' ')

f = FetchASNs()
f.get_asns(int(args[0]), int(args[1]))

print(sys.argv[1] + ' done')
sys.exit(0)
