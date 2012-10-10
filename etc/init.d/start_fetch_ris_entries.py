#!/usr/bin/python
# -*- coding: utf-8 -*-
# Inspired by : http://gitorious.org/forban/forban/blobs/master/bin/forbanctl

"""
Start the services fetching the (RIS) Whois information from the whois servers.
"""
import os
import sys
import ConfigParser

import signal
from pubsublogger import publisher
import argparse

servers_available = ['riswhois.ripe.net']

if __name__ == '__main__':

    publisher.channel = 'RISWhoisFetch'

    parser = argparse.ArgumentParser(description='Start the RIS Whoid fetcher processes')
    parser.add_argument('action', choices=('start', 'stop'))
    args = parser.parse_args()

    config = ConfigParser.RawConfigParser()
    config_file = "/etc/bgpranking/bgpranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
    from helpers.initscript import *
    services_dir = os.path.join(root_dir,config.get('directories','services'))

    service = os.path.join(services_dir, "fetch_ris_entries")

    if args.action == "start":
        publisher.info( "Starting fetching...")
        for option in servers_available:
            print(option + " to start...")
            publisher.info( option + " to start...")
            service_start_multiple(servicename = service,
                    param = ['-s', option],
                    number = int(config.get('processes','whois_fetch')))

    elif args.action == "stop":
        print("Stopping fetching...")
        publisher.info("Stopping fetching...")
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
    else:
        usage()
