import sys
import datetime 

try:
    import urllib.request, urllib.parse, urllib.error
except ImportError:
    import urllib
    
    
"""
Fetch the raw file
"""

def usage():
    print "raw_fetching.py dir url"
    exit (1)

if len(sys.argv) < 2:
    usage()

args = sys.argv[1].split(' ')

filename = args[0] + str(datetime.date.today())
urllib.urlretrieve(args[1], filename)

print('Fetching of ' + filename + ' done')
