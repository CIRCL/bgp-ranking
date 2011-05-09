#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    :file:`bin/services/db_input.py` - Database Input
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Move the new entries from the incoming to the storage database
"""

import os 
import sys
import ConfigParser
import syslog
import time


def usage():
    print "db_input.py"
    exit (1)


if __name__ == '__main__':
    
    config = ConfigParser.RawConfigParser()
    config_file = "/path/to/bgp-ranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
    from input_reader import InputReader
    sleep_timer = int(config.get('sleep_timers','short'))

    syslog.openlog('BGP_Ranking_DB_Input', syslog.LOG_PID, syslog.LOG_LOCAL5)

    reader = InputReader()
    reader.connect()

    while 1:
        try:
            if reader.insert():
                syslog.syslog(syslog.LOG_INFO, 'New entries inserted in Redis.')
        except:
            syslog.syslog(syslog.LOG_CRIT, 'Unable to insert, redis does not respond')
        time.sleep(sleep_timer)
    reader.disconnect()
