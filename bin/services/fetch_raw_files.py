#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    
    :file:`bin/services/fetch_raw_files.py` - Fetch the Raw files (datasets)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Fetch a raw file (given as paramater) and put it in a directory 
    (also a parameter) when finished, but only if the file is new.
    Elsewhere, the file is dropped. 
    
    During the download, the file is put in a temporary directory.
"""

import os 
import sys
import ConfigParser
import syslog
import datetime 
import urllib
import filecmp
import glob
import time
import redis


def usage():
    print "fetch_raw_files.py name dir url"
    exit (1)

class FetchRaw(object):

    def __init__(self, module, directory, url):
        config = ConfigParser.RawConfigParser()
        config_file = "/path/to/bgp-ranking.conf"
        config.read(config_file)
        root_dir = config.get('directories','root')
        raw_dir = config.get('directories','raw_data')
        temporary_dir = config.get('fetch_files','tmp_dir')
        old_dir = config.get('fetch_files','old_dir')

        self.sleep_timer = int(config.get('sleep_timers','long'))
        self.sleep_timer_short = int(config.get('sleep_timers','short'))

        self.config_db = redis.Redis(unix_socket_path = config.get('redis','unix_socket'),\
                                       db = config.get('redis','config'))

        self.module = module
        self.directory = os.path.join(root_dir, raw_dir, directory)
        self.url = url

        self.temp_filename = os.path.join(self.directory, temporary_dir, str(datetime.date.today()))
        self.filename = os.path.join(self.directory, str(datetime.date.today()))
        self.old_directory = os.path.join(self.directory, old_dir)

    def fetcher(self):
        """
            Main function which fetch the datasets
        """
        while self.config_db.sismember('modules', self.module):
            try:
                urllib.urlretrieve(self.url, self.temp_filename)
            except:
                syslog.syslog(syslog.LOG_ERR, 'Unable to fetch ' + self.url)
                self.check_exit()
                continue
            drop_file = False
            """
                Check is the file already exists, if the same file is found,
                the downloaded file is dropped. Else, it is moved in his final directory.
                FIXME: I should not check ALL the file present, or do sth with old files
            """
            to_check = glob.glob( os.path.join(self.old_directory, '*') )
            to_check += glob.glob( os.path.join(self.directory, '*') )
            for file in to_check:
                if filecmp.cmp(self.temp_filename, file):
                    drop_file = True
                    break
            if drop_file:
                os.unlink(self.temp_filename)
        #        syslog.syslog(syslog.LOG_DEBUG, 'No new file on ' + sys.argv[3])
            else:
                os.rename(self.temp_filename, self.filename)
                syslog.syslog(syslog.LOG_INFO, 'New file on ' + self.url)
            self.check_exit()
        self.config_db.delete(self.module + "|" + "fetching")

    def check_exit(self):
        """
            Check in redis if the module should be stoped
        """
        wait_until = datetime.datetime.now() + datetime.timedelta(seconds = self.sleep_timer)
        while wait_until >= datetime.datetime.now():
            if not self.config_db.sismember('modules', self.module):
                break
            time.sleep(self.sleep_timer_short)


if __name__ == '__main__':


    syslog.openlog('BGP_Ranking_Fetch_Raw_Files', syslog.LOG_PID, syslog.LOG_LOCAL5)

    if len(sys.argv) < 4:
        usage()

    fr = FetchRaw(sys.argv[1], sys.argv[2], sys.argv[3])

    fr.fetcher()
