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

if __name__ == '__main__':
    config = ConfigParser.RawConfigParser()
    config_file = "/path/to/bgp-ranking.conf"
    config.read(config_file)
    #sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

    # Temporary redis database
    temp_reris_db = int(config.get('modules_global','temp_db'))
    uid_var = config.get('modules_global','uid_var')
    uid_list = config.get('modules_global','uid_list')

class AbstractModule():
    """   
    To use this class you have to provide a variable called self.directory which is the directory 
    where the new files are. 
    
    A variable date is also necessary to move the file when the parsing is done. 
    
    You have to define a function parse which extract the entries from the dataset and use 
    the function put_entry to put them in redis. 
    """
    
    def __init__(self):
        self.separator = config.get('input_keys','separator')
        
        self.key_ip = config.get('input_keys','ip')
        self.key_src = config.get('input_keys','src')
        self.key_tstamp = config.get('input_keys','tstamp')
        self.key_infection = config.get('input_keys','infection')
        self.key_raw = config.get('input_keys','raw')
        self.key_times = config.get('input_keys','times')
        
        self.temp_db = redis.Redis(port = int(config.get('redis','port_cache')), db=temp_reris_db)
    
    def put_entry(self, entry):
        """
            Add the entries in the database
            
            entry is a dict:
            
                ::
                    
                    { ':ip' : ip , ':timestamp' : timestamp ... }
        """
        
        uid = self.temp_db.incr(uid_var)
        to_set = {}
        for key, value in entry.iteritems():
            if value is not None:
                to_set['{uid}{sep}{key}'.format(uid = str(uid),sep = self.separator, key = key)] = value
        pipeline = self.temp_db.pipeline(False)
        pipeline.mset(to_set)
        pipeline.sadd(uid_list, uid)
        pipeline.execute()

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

    def prepare_entry(self, ip, source, timestamp = None, infection = None, raw = None, times = None):
        """
            Prepare the entry to insert in redis
        """
        entry = {}
        entry[self.key_ip] = ip
        entry[self.key_src] = source
        entry[self.key_tstamp] = timestamp.isoformat()
        entry[self.key_infection] = infection
        entry[self.key_raw] = raw
        entry[self.key_times] = times
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
        new_filename = os.path.join(self.directory, config.get('fetch_files','old_dir'), str(self.date).replace(' ','-'))
        os.rename(file, new_filename)
