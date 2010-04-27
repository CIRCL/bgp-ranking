import sys
from whois.connector import Connector

def usage():
    print "whois_fetching.py server.tld"
    exit (1)

if len(sys.argv) < 2:
    usage()

c = Connector(sys.argv[1])
c.launch()
