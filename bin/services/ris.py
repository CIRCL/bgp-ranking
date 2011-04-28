#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

    :file:`bin/services/ris.py` - Push RIS Entries
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Process which push the RIS entries in redis
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
    from insert_ris import InsertRIS
    sleep_timer = int(config.get('sleep_timers','short'))

    syslog.openlog('BGP_Ranking_RIS_Whois_Insert', syslog.LOG_PID, syslog.LOG_LOCAL5)
    
    def usage():
        print "ris.py"
        exit (1)

    insertor = InsertRIS()

    while 1:
        if insertor.get_ris():
            syslog.syslog(syslog.LOG_INFO, 'New RIS entries inserted in Redis.')
        time.sleep(sleep_timer)
