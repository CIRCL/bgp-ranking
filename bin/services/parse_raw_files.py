#!/usr/bin/python
import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('global','root')
sys.path.append(os.path.join(root_dir,config.get('global','lib')))
raw_data = os.path.join(root_dir,config.get('global','raw_data'))
sleep_timer = int(config.get('global','sleep_timer_short'))

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename=os.path.join(root_dir,config.get('logging','log_parse_raw_files')))

from modules import *

import time

"""
Parse the file of a module
"""

def usage():
    print "parse_raw_files.py name"
    exit (1)

if len(sys.argv) < 2:
    usage()

while 1:
    module = eval(sys.argv[1])(raw_data)
    if module.update():
        print('Done with ' + sys.argv[1])
        logging.info('Done with ' + sys.argv[1])
    else:
        print('No files to parse for ' + sys.argv[1])
        logging.info('No files to parse for ' + sys.argv[1])
    time.sleep(sleep_timer)
