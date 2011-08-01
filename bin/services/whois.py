#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

    :file:`bin/services/whois.py` - Push Whois Entries
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Process which push the Whois entries in redis
"""
import os
import sys
import ConfigParser
import syslog
import time


if __name__ == '__main__':

    config = ConfigParser.RawConfigParser()
    config_file = "/path/to/bgp-ranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
    from insert_whois import InsertWhois
    sleep_timer = int(config.get('sleep_timers','short'))

    syslog.openlog('BGP_Ranking_Whois_Insert', syslog.LOG_PID, syslog.LOG_LOCAL5)

    def usage():
        print "whois.py"
        exit (1)

    insertor = InsertWhois()

    while 1:
        if insertor.get_whois():
            syslog.syslog(syslog.LOG_INFO, 'New Whois entries inserted in Redis.')
        time.sleep(sleep_timer)
