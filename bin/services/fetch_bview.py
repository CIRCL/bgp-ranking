#!/usr/bin/python

"""
The service fetch a dump of the routing database from 
the RIS Whois service provided by RIPE NCC.

It verifies if the new file is more recent than the one already downloaded. 
When the script is started, the most recent dump is inconditionally downloaded. 

The URL to download looks like that: 
http://data.ris.ripe.net/rrc00/YYYY.MM/bview.YYYYMMDD.HHHH.gz
YYYY    = Year (e.g. 2010)
MM      = Month (e.g. 09)
DD      = Day (e.g. 01)
HHHH    = Hour (0000, 0800 or 1600)

We always want to fetch the latest available dump, the script will take 
the current day and try to find a file corresponding to one of the three possible hours, 
in reverse order. 

If the script is not restarted, it will never download two time the same file: 
the hour corresponding the last downloaded file is saved. 
Note: When the current day change, this hour is set to None. 

"""

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

def usage():
    print "fetch_bview.py"
    exit (1)

base_url = config.get('routing','base_url')
hours = sorted(config.get('routing','update_hours').split())
prefix = config.get('routing','prefix_basename')
suffix = config.get('routing','suffix_basename')


"""
To verify if the URL to fetch exists, we use a function provided by the two following links 
- http://code.activestate.com/recipes/101276/ and 
- http://stackoverflow.com/questions/2486145/python-check-if-url-to-jpg-exists
"""
import httplib
from urlparse import urlparse 

def checkURL(url): 
    """
    Check if the URL exists by getting the header of the response.
    """
    p = urlparse(url) 
    h = httplib.HTTPConnection(p[1]) 
    h.request('HEAD', p[2])
    reply = h.getresponse()
    h.close()
    if reply.status == 200 : return 1 
    else: return 0 



def downloadURL(url):
    """
    Inconditianilly download the URL in a temporary directory.
    When finished, the file is moved in the real directory. 
    Like this an other process will not attempt to extract an inclomplete file.
    """
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
        # If the script just startor if the current day change, the hour is set to None
        last_hour = None
    # Initialization of the URL to fetch
    dir = current_date.strftime("%Y.%m")
    file_day = current_date.strftime("%Y%m%d")
    daily_url = base_url + '/' + dir + '/' + prefix + file_day + '.%s' +  suffix

    for hour in reversed(hours):
        # Check if there is a file available for the possible hours. 
        if last_hour == hour and last_date == current_date:
            break
        url = daily_url % hour
        if checkURL(url):
            syslog.syslog(syslog.LOG_INFO, "New bview file found: " + url)
            downloadURL(url)
            last_hour = hour
            break
    time.sleep(sleep_timer)
