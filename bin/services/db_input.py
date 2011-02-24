#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    BGP Ranking - Script - Database Input
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Move the new entries from the incoming to the storage database

    :copyright: Copyright 2010-2011 by the BGP Ranking team, see :file:`AUTHORS`.
    :licence: AGPL3, see :file:`LICENSE` for details.
"""

def usage():
    print "db_input.py"
    exit (1)

if __name__ == '__main__':
    import os 
    import sys
    import ConfigParser
    import syslog
    
    config = ConfigParser.RawConfigParser()
    config_file = "/home/rvinot/bgp-ranking/etc/bgp-ranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
    sleep_timer = int(config.get('sleep_timers','short'))

    syslog.openlog('BGP_Ranking_DB_Input', syslog.LOG_PID, syslog.LOG_USER)

    from input_reader import InputReader
    import time

    reader = InputReader()
    reader.connect()

    while 1:
        if reader.insert():
            syslog.syslog(syslog.LOG_INFO, 'New entries inserted in Redis.')
        time.sleep(sleep_timer)

    reader.disconnect()
