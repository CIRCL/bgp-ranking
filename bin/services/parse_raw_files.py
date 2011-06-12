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
import syslog
import time
import redis


def usage():
    print "parse_raw_files.py name dir"
    exit (1)

if __name__ == '__main__':

    config = ConfigParser.RawConfigParser()
    config_file = "/path/to/bgp-ranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
    from modules import *
    raw_data = os.path.join(root_dir,config.get('directories','raw_data'))
    sleep_timer = int(config.get('sleep_timers','short'))
    config_db = redis.Redis(unix_socket_path = config.get('redis','unix_socket'),\
                              db = config.get('redis','config'))

    syslog.openlog('BGP_Ranking_Get_Whois_Entries', syslog.LOG_PID, syslog.LOG_LOCAL5)

    if len(sys.argv) < 3:
        usage()

    directory = os.path.join(raw_data, sys.argv[2])

    module = eval(sys.argv[1])(directory)
    while config_db.sismember('modules', sys.argv[1]):
        if module.update():
            syslog.syslog(syslog.LOG_INFO, 'Done with ' + sys.argv[1])
        else:
    #        syslog.syslog(syslog.LOG_DEBUG, 'No files to parse for ' + sys.argv[1])
            pass
        time.sleep(sleep_timer)
    config_db.delete(sys.argv[1] + "|" + "parsing")
