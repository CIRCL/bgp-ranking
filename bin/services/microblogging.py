#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    :file:`bin/services/microblog.py` - Microblogging client
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Start the microblogging client which posts on twitter and identica
"""

import os 
import sys
import ConfigParser
import syslog
import time


def usage():
    print "microblogging.py"
    exit (1)


if __name__ == '__main__':
    
    config = ConfigParser.RawConfigParser()
    config_file = "/path/to/bgp-ranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
    from microblog.micro_blog import MicroBlog
    sleep_timer = int(config.get('sleep_timers','intermediate'))

    syslog.openlog('BGP_Ranking_Microblog', syslog.LOG_PID, syslog.LOG_LOCAL5)

    mb = MicroBlog()

    while 1:
        try:
            if mb.post_last_top():
                syslog.syslog(syslog.LOG_INFO, 'New Ranking posted on twitter and identica.')
            mb.grab_dms(mb.twitter_api, mb.last_dm_twitter_key)
            mb.grab_dms(mb.identica_api, mb.last_dm_identica_key)
        except:
            pass
        time.sleep(sleep_timer)
    reader.disconnect()
