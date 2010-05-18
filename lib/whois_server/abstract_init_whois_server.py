#!/usr/bin/python

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('global','root')
whois_db = os.path.join(root_dir,config.get('global','whois_db'))
unpack_dir = os.path.join(root_dir,config.get('whois_server','unpack_dir'))
use_tmpfs = int(config.get('whois_server','use_tmpfs'))

import re
import redis 
from abc import ABCMeta, abstractmethod

import gc

class InitWhoisServer:
    """
    Generic functions to initialize the redis database for a particular whois server. 
    This class needs some variables: 
    - keys: the list of keys of the database 
        format: [[ '^key', [] ] , [ '^key', [] ] ... ]
    - archive_name: the name of the db dump, gzip compressed
    - dump_name: the name of the db dump, extracted
    """
    
    max_pending_keys = 1000000
    pending_keys = 0
    
    __metaclass__ = ABCMeta    
    @abstractmethod
    def push_helper_keys(self, key, redis_key, entry):
        """
        Push all helper keys for a particular whois source
        for example: push a network corresponding to a particular entry
        """
        pass
    
    def __init__(self):
        config = ConfigParser.RawConfigParser()
        config.read("../../etc/bgp-ranking.conf")
        self.root_dir = config.get('global','root')
        self.whois_db = os.path.join(root_dir,config.get('global','whois_db'))
        self.unpack_dir = os.path.join(root_dir,config.get('whois_server','unpack_dir'))
        self.use_tmpfs = int(config.get('whois_server','use_tmpfs'))
        if self.use_tmpfs:
            tmpfs_size = config.get('whois_server','tmpfs_size')
            if not os.path.ismount(unpack_dir):
#                print('Mount the tmpfs directory')
                os.popen('mount -t tmpfs -o size=' + tmpfs_size + ' tmpfs ' + unpack_dir)
        self.extracted = os.path.join(self.unpack_dir,self.dump_name)

    def start(self):
#        self.prepare()
        self.dispatch_by_key()
        self.push_into_db()
        self.clean_system()
    
    def prepare(self):
        archive = os.path.join(self.whois_db,self.archive_name)
        os.popen('gunzip -c ' + archive + ' > ' + self.extracted)
    
    def dispatch_by_key(self):
        file = open(self.extracted)
        entry = ''
        for line in file:
            if line == '\n':
                if len(entry) > 0 and not re.match('^#', entry):
                    key_found = False
                    for key, entries in self.keys:
                        if re.match(key, entry):
                            entries.append(entry)
                            key_found = True
                            break
                    if not key_found:
                        errors.append(entry)
                entry = ''
                self.pending_keys += 1
                if self.pending_keys >= self.max_pending_keys:
                    self.push_into_db()
            else :
                entry += line
    
    def push_into_db(self):
        self.redis_whois_server = redis.Redis(db=int(config.get('whois_server','redis_db')) )
        for key,entries in self.keys:
#            print('Begin' + key)
            while len(entries) > 0 :
                entry = entries.pop()
                # TODO: remode replace when redis support ' ' in a key 
                redis_key = re.findall(key + '[ \t]*(.*)', entry)[0].replace(' ', '_')
                self.redis_whois_server.set(redis_key, entry)
                self.push_helper_keys(key, redis_key, entry)
        self.pending_keys = 0
    
    def clean_system(self):
        if self.use_tmpfs:
            if os.path.ismount(self.unpack_dir):
                print('Umount the tmpfs directory')
                os.popen('umount ' + self.unpack_dir)
        else:
#            os.unlink(extracted)
            pass
