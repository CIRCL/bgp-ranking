#!/usr/bin/python
# -*- coding: utf-8 -*-

import redis
import ConfigParser
import glob
import os
import datetime
import re
import importlib
import sys

separator = '|'
key_ip = 'ip'
key_src = 'source'
key_tstamp = 'timestamp'

key_uid = 'uid'
key_uid_list = 'uid_list'

old_dir = 'old'

temp_db = None

def __prepare():
    global temp_db

    config = ConfigParser.RawConfigParser()
    config_file = "/etc/bgpranking/bgpranking.conf"
    config.read(config_file)

    temp_db = redis.Redis(port = int(config.get('redis','port_cache')),
            db=int(config.get('modules_global','temp_db')))
    sys.path.append(os.path.dirname(__file__))

def new_entry(ip, source, timestamp):
    """
        insert a new entry in redis
    """
    if temp_db is None:
        __prepare()
    uid = temp_db.incr(key_uid)
    p = temp_db.pipeline()
    p.hmset(uid, {key_ip: ip, key_src: source, key_tstamp: timestamp})
    p.sadd(key_uid_list, uid)
    p.execute()

def __get_files(directory):
    """
    Select all the files in directory (ie. not the directories)
    and return a list.
    """
    allfiles = glob.glob(directory + '/*')
    files = []
    for f in allfiles:
        if not os.path.isdir(f):
            files.append(f)
    return files

def __default_parser(filename, listname, date):
    """
        Search for IPs on each line of the files in that dir
    """
    with open(filename, 'r') as f:
        for line in f:
            ip = re.findall('((?:\d{1,3}\.){3}\d{1,3})',line)
            if len(ip) == 0:
                continue
            new_entry(ip[0], listname, date)
    return date

def importer(raw_dir, listname):
    has_files = False
    if temp_db is None:
        __prepare()
    try:
        parser = importlib.import_module(listname).parser
    except:
        parser = __default_parser
    date = datetime.date.today()
    for filename in __get_files(raw_dir):
        has_files = True
        date_from_module = parser(filename, listname, date)
        if date_from_module is not None:
            date = date_from_module
        os.rename(filename,
                os.path.join(raw_dir, old_dir, str(date).replace(' ','-')))
    return has_files
