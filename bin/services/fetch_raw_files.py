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
import ConfigParser
from pubsublogger import publisher
import argparse
import datetime
import urllib
import filecmp
import glob
import time
import redis
import socket

sleep_timer = 0
sleep_timer_short = 0
config_db = None
module = None
directory = None
url = None
temp_filename = None
filename = None
old_directory = None

def prepare():
    global sleep_timer
    global sleep_timer_short
    global config_db
    global directory
    global temp_filename
    global filename
    global old_directory
    config = ConfigParser.RawConfigParser()
    config_file = '/etc/bgpranking/bgpranking.conf'
    config.read(config_file)

    root_dir = config.get('directories','root')
    raw_dir = config.get('directories','raw_data')
    directory = os.path.join(root_dir, raw_dir, directory)
    filename = os.path.join(directory, str(datetime.date.today()))

    temporary_dir = config.get('fetch_files','tmp_dir')
    temp_filename = os.path.join(directory, temporary_dir, str(datetime.date.today()))

    old_dir = config.get('fetch_files','old_dir')
    old_directory = os.path.join(directory, old_dir)

    sleep_timer = int(config.get('sleep_timers','long'))
    sleep_timer_short = int(config.get('sleep_timers','short'))

    config_db = redis.Redis(port = int(config.get('redis','port_master')),\
                                   db = config.get('redis','config'))
    socket.setdefaulttimeout(120)


def fetcher():
    """
        Main function which fetch the datasets
    """
    while config_db.sismember('modules', module):
        try:
            urllib.urlretrieve(url, temp_filename)
        except:
            publisher.error('Unable to fetch ' + url)
            __check_exit()
            continue
        drop_file = False
        """
            Check is the file already exists, if the same file is found,
            the downloaded file is dropped. Else, it is moved in his final directory.
            FIXME: I should not check ALL the file present, or do sth with old files
        """
        to_check = glob.glob( os.path.join(old_directory, '*') )
        to_check += glob.glob( os.path.join(directory, '*') )
        for file in to_check:
            if filecmp.cmp(temp_filename, file):
                drop_file = True
                break
        if drop_file:
            os.unlink(temp_filename)
            publisher.debug('No new file on ' + url)
        else:
            os.rename(temp_filename, filename)
            publisher.info('New file on ' + url)
        __check_exit()
    config_db.delete(module + "|" + "fetching")

def __check_exit():
    """
        Check in redis if the module should be stoped
    """
    wait_until = datetime.datetime.now() + datetime.timedelta(seconds = sleep_timer)
    while wait_until >= datetime.datetime.now():
        if not config_db.sismember('modules', module):
            break
        time.sleep(sleep_timer_short)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start a fetcher for a list.')

    parser.add_argument("-n", "--name", required=True, type=str, help='Name of the list.')
    parser.add_argument("-d", "--directory", required=True, type=str, help='Path to the directory where the lists are saved.')
    parser.add_argument("-u", "--url", required=True, type=str, help='URL to fetch.')

    args = parser.parse_args()

    module = args.name
    directory = args.directory
    url = args.url

    publisher.channel = 'FetchRawFiles'

    prepare()
    fetcher()

