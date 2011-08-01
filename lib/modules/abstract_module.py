#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Abstract class of the modules
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This abstract class should be used by all local modules. Local means that the modules
    are running on the same server as the redis databases.
"""


from abc import ABCMeta, abstractmethod

import redis
import glob

import os
import sys
import ConfigParser

class AbstractModule(object):
    """
    To use this class you have to provide a variable called self.directory which is the directory
    where the new files are.

    A variable date is also necessary to move the file when the parsing is done.

    You have to define a function parse which extract the entries from the dataset and use
    the function put_entry to put them in redis.
    """

    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        config_file = "/path/to/bgp-ranking.conf"
        self.config.read(config_file)

        self.separator = self.config.get('input_keys','separator')

        self.key_ip = self.config.get('input_keys','ip')
        self.key_src = self.config.get('input_keys','src')
        self.key_tstamp = self.config.get('input_keys','tstamp')

        self.temp_db = redis.Redis(port = int(self.config.get('redis','port_cache')),\
                            db=int(self.config.get('modules_global','temp_db')))

    def put_entry(self, entry):
        """
            Add the entries in the database
            entry is a dict:
                ::
                    { 'ip' : ip , 'timestamp' : timestamp ... }
        """

        uid = self.temp_db.incr(self.config.get('modules_global','uid_var'))
        self.temp_db.hmset(uid, entry)
        self.temp_db.sadd(self.config.get('modules_global','uid_list'), uid)

    def glob_only_files(self):
        """
            Select all the files in self.directory (ie. not the directories) and initalize a variable
            self.files.
        """
        allfiles = glob.glob( self.directory + '/*')
        self.files = []
        for file in allfiles:
            if not os.path.isdir(file):
                self.files.append(file)

    def prepare_entry(self, ip, source, timestamp):
        """
            Prepare the entry to insert in redis
        """
        entry = {}
        entry[self.key_ip] = ip
        entry[self.key_src] = source
        entry[self.key_tstamp] = timestamp.isoformat()
        return entry

    __metaclass__ = ABCMeta
    @abstractmethod
    def parse(self):
        """
        Extract the entries from the dataset and use the function put_entry to put them in redis
        """
        pass

    def update(self):
        """
        Parse the files and put the information in redis
        """
        self.glob_only_files()
        if len(self.files) > 0:
            self.parse()

    def move_file(self, file):
        """
        Move /from/some/dir/file to /from/some/dir/old/file
        """
        new_filename = os.path.join(self.directory, self.config.get('fetch_files','old_dir'), str(self.date).replace(' ','-'))
        os.rename(file, new_filename)
