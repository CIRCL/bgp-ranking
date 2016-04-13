#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

    :file:`bin/services/parse_raw_files.py` - Parse a raw dataset
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Launch the parsing of a raw file.
"""
import os
import sys
import ConfigParser
import time
import redis
from pubsublogger import publisher
import argparse


if __name__ == '__main__':

    publisher.channel = 'ParseRawFiles'
    parser = argparse.ArgumentParser(description='Start a parser.')
    parser.add_argument("-n", "--name", required=True, type=str,
            help='Name of the list.')
    parser.add_argument("-d", "--directory", required=True, type=str,
            help='Path to the directory where the lists are saved.')
    parser.add_argument("-t", "--timer", required=True, type=int,
            help='Interval between two checks for files to parse.')

    args = parser.parse_args()


    config = ConfigParser.RawConfigParser()
    config_file = '/etc/bgpranking/bgpranking.conf'
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
    from modules import helper
    raw_data = os.path.join(root_dir,config.get('directories','raw_data'))
    config_db = redis.Redis(host=config.get('redis','host_master2'),
                            port = int(config.get('redis','port_master2')),\
                            db = config.get('redis','config'))

    directory = os.path.join(raw_data, args.directory)

    while config_db.sismember('modules', args.name):
        if helper.importer(directory, args.name):
            publisher.info('Done with ' + args.name)
        else:
            publisher.debug('No files to parse for ' + args.name)
        time.sleep(args.timer)
    config_db.delete(args.name + "|" + "parsing")
