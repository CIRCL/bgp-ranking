
from abc import ABCMeta, abstractmethod

import redis
import glob

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
#sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

# Temporary redis database
temp_reris_db = int(config.get('modules_global','temp_db'))
uid_var = config.get('modules_global','uid_var')
list_ips = config.get('modules_global','uid_list')

class AbstractModule():
    """
    This abstract class should be used by all local modules. Local means that the modules 
    does not send their entries through the network. 
    
    To use this class you have to provide a variable called self.directory which is the directory 
    where the new files are. 
    A variable date is also necessary to move the file when the parsing is done. 
    You have to define a function parse which extract the entries from the dataset and use 
    the function put_entry to put them in redis. 
    """
    key_ip = config.get('input_keys','ip')
    key_src = config.get('input_keys','src')
    key_tstamp = config.get('input_keys','tstamp')
    key_infection = config.get('input_keys','infection')
    key_raw = config.get('input_keys','raw')
    key_times = config.get('input_keys','times')
    
    def __init__(self):
        self.temp_db = redis.Redis(db=temp_reris_db)
    
    def put_entry(self, entry):
        uid = self.temp_db.incr(uid_var)
        # the format of "entry" is : { ':ip' : ip , ':timestamp' : timestamp ... }
        for key, value in entry.iteritems():
            if value is not None:
                self.temp_db.set(str(uid) + key, value)
        self.temp_db.sadd(list_ips, uid)

    def __glob_only_files(self):
        allfiles = glob.glob( self.directory + '/*')
        self.files = []
        for file in allfiles:
            if not os.path.isdir(file):
                self.files.append(file)

    def prepare_entry(self, ip, source, timestamp = None, infection = None, raw = None, times = None):
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
        self.__glob_only_files()
        if len(self.files) > 0:
            self.parse()
        
    def move_file(self, file):
        """
        Move /from/some/dir/file to /from/some/dir/old/file
        """
        new_filename = os.path.join(self.directory, config.get('fetch_files','old_dir'), str(self.date).replace(' ','-'))
        os.rename(file, new_filename)