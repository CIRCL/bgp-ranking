#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

"""
Start the service fetching the dumps of routing information (bview files)
provided by RIPE NCC
"""
import os
import sys
import ConfigParser

import signal
from pubsublogger import publisher
import argparse

if __name__ == '__main__':

    publisher.channel = 'Ranking'

    parser = argparse.ArgumentParser(description='Fetch a Bview file.')
    parser.add_argument('action', choices=('start', 'stop'))
    args = parser.parse_args()

    config = ConfigParser.RawConfigParser()
    config_file = '/etc/bgpranking/bgpranking.conf'
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
    from helpers.initscript import *
    services_dir = os.path.join(root_dir,config.get('directories','services'))

    service = os.path.join(services_dir, "fetch_bview")

    if args.action == "start":
        print('Start fetching of bview')
        publisher.info('Start fetching of bview')
        print(service + " to start...")
        publisher.info(service + " to start...")
        proc = service_start_once(servicename = service,
                processname = service)

    elif args.action == "stop":
        print('Stop fetching of bview')
        publisher.info('Stop fetching of bview')
        pid = pidof(processname=service)
        if pid:
            pid = pid[0]
            print(service + " to be stopped...")
            publisher.info(service + " to be stopped...")
            try:
                os.kill(int(pid), signal.SIGKILL)
            except OSError, e:
                print(service + 'unsuccessfully stopped')
                publisher.error(service + 'unsuccessfully stopped')
            rmpid(processname=service)
