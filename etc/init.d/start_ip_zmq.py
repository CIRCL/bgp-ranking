#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

"""
Start the module manager
"""
import os
import sys
import ConfigParser

import signal
from pubsublogger import publisher
import argparse


if __name__ == '__main__':

    publisher.channel = 'ModuleManager'

    parser = argparse.ArgumentParser(description='Start the ZeroMQ IP publisher.')
    parser.add_argument('action', choices=('start', 'stop'))
    args = parser.parse_args()

    config = ConfigParser.RawConfigParser()
    config_file = "/etc/bgpranking/bgpranking.conf"
    config.read(config_file)
    root_dir = config.get('directories', 'root')
    sys.path.append(os.path.join(root_dir, config.get('directories', 'libraries')))
    from helpers.initscript import *
    services_dir = os.path.join(root_dir, config.get('directories', 'services'))

    service = os.path.join(services_dir, "ip_zmq")

    if args.action == "start":
        print("Starting ZeroMQ IP publisher...")
        publisher.info('Starting ZeroMQ IP publisher...')
        print(service+" to start...")
        publisher.info(service + 'to start...')
        proc = service_start_once(servicename=service, processname=service)

    elif args.action == "stop":
        print("Stopping ZeroMQ IP publisher...")
        publisher.info('Stopping ZeroMQ IP publisher...')
        pid = pidof(processname=service)
        if pid:
            pid = pid[0]
            try:
                os.kill(int(pid), signal.SIGHUP)
            except OSError, e:
                print(service + " unsuccessfully stopped")
                publisher.error(service + 'unsuccessfully stopped')
            rmpid(processname=service)
        else:
            print('No running ZeroMQ IP publisher process')
            publisher.info('No running ZeroMQ IP publisher process')
