#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    
    BGP Ranking - Script - Fetch the Raw files (datasets)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Fetch a raw file (given as paramater) and put it in a directory 
    (also a parameter) when finished, but only if the file is new.
    Elsewhere, the file is dropped. 
    
    During the download, the file is put in a temporary directory.
"""

def usage():
    print "fetch_raw_files.py dir url"
    exit (1)

if __name__ == '__main__':

    import os 
    import sys
    import ConfigParser
    config = ConfigParser.RawConfigParser()
    config_file = "/home/rvinot/bgp-ranking/etc/bgp-ranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    temporary_dir = config.get('fetch_files','tmp_dir')
    old_dir = config.get('fetch_files','old_dir')
    sleep_timer = int(config.get('sleep_timers','long'))

    import syslog
    syslog.openlog('BGP_Ranking_Fetch_Raw_Files', syslog.LOG_PID, syslog.LOG_USER)

    import datetime 
    import urllib
    import filecmp
    import glob
    import time


    if len(sys.argv) < 2:
        usage()

    args = sys.argv[1].split(' ')

    temp_filename = os.path.join(args[0], temporary_dir, str(datetime.date.today()))
    filename = os.path.join(args[0], str(datetime.date.today()))
    old_directory = os.path.join(args[0], old_dir)

    while 1:
        try:
            urllib.urlretrieve(args[1], temp_filename)
        except:
            syslog.syslog(syslog.LOG_ERR, 'Unable to fetch ' + args[1])
            time.sleep(sleep_timer)
            continue
        drop_file = False
        """
        Check is the file already exists, if the same file is found, 
        the downloaded file is dropped. Else, it is moved in his final directory. 
        FIXME: I should not check ALL the file present, or do sth with old files 
        """
        to_check = glob.glob( os.path.join(old_directory, '*') )
        to_check += glob.glob( os.path.join(args[0], '*') )
        for file in to_check:
            if filecmp.cmp(temp_filename, file):
                drop_file = True
                break
        if drop_file:
            os.unlink(temp_filename)
    #        syslog.syslog(syslog.LOG_DEBUG, 'No new file on ' + args[1])
        else:
            os.rename(temp_filename, filename)
            syslog.syslog(syslog.LOG_INFO, 'New file on ' + args[1])
        time.sleep(sleep_timer)
