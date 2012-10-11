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
import time
from pubsublogger import publisher

dev_mode = True

if __name__ == '__main__':

    config = ConfigParser.RawConfigParser()
    config_file = "/etc/bgpranking/bgpranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
    from microblog.micro_blog import MicroBlog
    sleep_timer = int(config.get('sleep_timers','intermediate'))

    publisher.channel = 'Ranking'

    mb = MicroBlog()

    while 1:
        try:
            if mb.post_last_top(dev_mode):
                publisher.info('New Ranking posted on twitter and identica.')
            mb.grab_dms(mb.twitter_api, mb.last_dm_twitter_key)
            mb.grab_dms(mb.identica_api, mb.last_dm_identica_key)
        except Exception as e:
            publisher.error('The microblog module was sad: ' + e.strerror)
        time.sleep(sleep_timer)
