#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    
    Module Manager
    ~~~~~~~~~~~~~~

    Manage the modules :)
     * Fetching
     * Parsing
"""
import os 
import sys
import ConfigParser
import syslog
import time
import redis


def usage():
    print "module_manager.py"
    exit (1)

if __name__ == '__main__':

    config = ConfigParser.RawConfigParser()
    config_file = "/path/to/bgp-ranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
    config_db = redis.Redis(port = int(self.config.get('redis','port_master')),\
                                       db = self.config.get('redis','config'))
    
    modules = config_db.smembers('modules')
    