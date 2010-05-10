#!/usr/bin/python

import datetime 
import sys

try:
    import urllib.request, urllib.parse, urllib.error
except ImportError:
    import urllib
import os 
import filecmp
import glob
import time
    
"""
Fetch the raw file
"""

temporary_dir = 'temp'
sleep_timer = 5

def usage():
    print "fetch_raw_files.py dir url"
    exit (1)

if len(sys.argv) < 2:
    usage()

args = sys.argv[1].split(' ')

temp_filename = os.path.join(args[0], temporary_dir,  str(datetime.date.today()))
filename = os.path.join(args[0], str(datetime.date.today()))
old_directory = os.path.join(args[0], 'old')


while 1:
    urllib.urlretrieve(args[1], temp_filename)
    drop_file = False
    to_check = glob.glob( old_directory + '/*')
    to_check += glob.glob(args[0] + '/*')
    for file in to_check:
        if filecmp.cmp(temp_filename, file):
            drop_file = True
            break
    if drop_file:
        print('No new file on ' + args[1])
        os.unlink(temp_filename)
    else:
        print('New file on ' + args[1])
        os.rename(temp_filename, filename)
    time.sleep(sleep_timer)
