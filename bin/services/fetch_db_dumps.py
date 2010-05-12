#!/usr/bin/python

import datetime
import filecmp
import glob
import time

try:
    import urllib.request, urllib.parse, urllib.error
except ImportError:
    import urllib
import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../bgp-ranking.conf")
whois_dir = os.path.join(config.get('global','root'),config.get('global','whois_db'))
    
"""
Fetch the db dump
"""

temporary_dir = os.path.join(whois_dir, 'temp')
sleep_timer = 5

def usage():
    print "fetch_db_dumps.py serial url"
    exit (1)

if len(sys.argv) < 2:
    usage()

args = sys.argv[1].split(' ')
serial_name = os.path.basename(args[0])
db_name = os.path.basename(args[1])
temporary_serial_file = os.path.join(temporary_dir, serial_name)
serial_file = os.path.join(whois_dir, serial_name)
temporary_db_file = os.path.join(temporary_dir, db_name)
db_file = os.path.join(whois_dir, db_name)

while 1:
    urllib.urlretrieve(args[0], temporary_serial_file)
    new_db = True
    if os.path.exists(serial_file) and filecmp.cmp(temporary_serial_file, serial_file):
        new_db = False
    if new_db:
        print('New ' + db_name)
        urllib.urlretrieve(args[1], temporary_db_file)
        os.rename(temporary_serial_file, serial_file)
        os.rename(temporary_db_file, db_file)
    else:
        print('No New' + db_name)
    time.sleep(sleep_timer)
