#!/usr/bin/python
import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('directories','root')
temporary_dir = config.get('fetch_files','tmp_dir')
old_dir = config.get('fetch_files','old_dir')
sleep_timer = int(config.get('routing','timer'))
raw_data = os.path.join(root_dir,config.get('directories','raw_data'))

import syslog
syslog.openlog('BGP_Ranking_Fetch_bview', syslog.LOG_PID, syslog.LOG_USER)

import datetime 
import urllib
import filecmp
import glob
import time
    
"""
Fetch the raw file
"""

def usage():
    print "fetch_bview.py"
    exit (1)

base_url = config.get('routing','base_url')
hours = sorted(config.get('routing','update_hours').split())
prefix = config.get('routing','prefix_basename')
suffix = config.get('routing','suffix_basename')

# http://code.activestate.com/recipes/101276/ and 
# http://stackoverflow.com/questions/2486145/python-check-if-url-to-jpg-exists
import httplib
from urlparse import urlparse 

def checkURL(url): 
     p = urlparse(url) 
     h = httplib.HTTPConnection(p[1]) 
     h.request('HEAD', p[2])
     reply = h.getresponse()
     h.close()
     if reply.status == 200 : return 1 
     else: return 0 
# end

def downloadURL(url):
    tmp_dest_file = os.path.join(raw_data, config.get('routing','temp_bviewfile'))
    dest_file = os.path.join(raw_data, config.get('routing','bviewfile'))
    urllib.urlretrieve(url, tmp_dest_file)
    os.rename(tmp_dest_file, dest_file)

last_hour = None
current_date = None
while 1:
    last_date = current_date
    current_date = datetime.date.today()
    if last_date != current_date:
        last_hour = None
    dir = current_date.strftime("%Y.%m")
    file_day = current_date.strftime("%Y%m%d")
    daily_url = base_url + '/' + dir + '/' + prefix + file_day + '.%s' +  suffix

    for hour in reversed(hours):
        if last_hour == hour and last_date == current_date:
            break
        url = daily_url % hour
        if checkURL(url):
            syslog.syslog(syslog.LOG_INFO, "New bview file found: " + url)
            downloadURL(url)
            last_hour = hour
            break
    time.sleep(sleep_timer)
