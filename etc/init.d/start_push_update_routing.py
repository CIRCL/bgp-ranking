#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

"""
Start the process pushing the update of the routing information.
NOTE: it will also compute the ranking
"""
import os
import sys
import ConfigParser

import signal
from pubsublogger import publisher
import argparse

if __name__ == '__main__':

    publisher.channel = 'Ranking'

    parser = argparse.ArgumentParser(description='Start a Bview file processor, and run the ranking process.')
    parser.add_argument('action', choices=('start', 'stop'))
    args = parser.parse_args()

    config = ConfigParser.RawConfigParser()
    config_file = "/etc/bgpranking/bgpranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

    from helpers.initscript import *
    from helpers.files_splitter import *
    services_dir = os.path.join(root_dir,config.get('directories','services'))
    raw_data = os.path.join(root_dir,config.get('directories','raw_data'))

    service = os.path.join(services_dir, "push_update_routing")

    if args.action == "start":
        print("Start pushing routes...")
        publisher.info( "Start pushing routes...")
        print(service + " to start...")
        publisher.info(service + " to start...")
        proc = service_start_once(servicename = service,
                processname = service)

    elif args.action == "stop":
        print("Stop pushing routes...")
        publisher.info("Stop pushing routes...")
        pids = pidof(processname=service)
        if pids:
            print(service + " to be stopped...")
            publisher.info(service + " to be stopped...")
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGKILL)
                except OSError, e:
                    print(service + " unsuccessfully stopped")
                    publisher.error(service + " unsuccessfully stopped")
            rmpid(processname=service)

