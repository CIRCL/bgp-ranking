#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

    Module Manager
    ~~~~~~~~~~~~~~

    Manage the modules :)
     * Fetching
     * Parsing

    .. note::
        To start correctly, each module needs:

            * The list of modules (parser and fetcher)
            * $HOME of each module (parser and fetcher)
            * The URL where is the file to fetch (fetcher)
"""
import os
import sys
import ConfigParser
import time
import redis
import subprocess
from pubsublogger import publisher


config_db = None
services_dir = None
sleep_timer = 30

def prepare():
    global config_db
    global services_dir
    config = ConfigParser.RawConfigParser()
    config_file = '/etc/bgpranking/bgpranking.conf'
    config.read(config_file)


    root_dir = config.get('directories','root')
    services_dir = os.path.join(root_dir,config.get('directories','services'))
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

    config_db = redis.Redis(port = int(config.get('redis','port_master')),\
                                   db = config.get('redis','config'))


def launch_fetcher(module):
    """
        Launch a process which fetch a dataset in a directory
    """
    service_fetcher = os.path.join(services_dir, "fetch_raw_files.py")
    timer = 3600
    if module is None:
        publisher.error('Unable to start fetching : module is None')
        return
    url = config_db.get(module + "|" + "url")
    if url is None:
        publisher.info(module + ' does not have an URL, no fetcher.')
        config_db.set(module + "|" + "fetching", 0)
        return
    directory = config_db.get(module + "|" + "home_dir")
    if directory is not None:
        subprocess.Popen(["python", service_fetcher, '-n', module,
            '-d', directory, '-u', url, '-t', timer])
        config_db.set(module + "|" + "fetching", 1)
        publisher.info('Fetching of ' + module + 'started.')
    else:
        publisher.error('Unable to start fetching of ' + module + \
                ': home_dir unknown.')
        config_db.set(module + "|" + "fetching", 0)


def launch_parser(module):
    """
        Launch a parser on a dataset for a module
    """
    service_parser = os.path.join(services_dir, "parse_raw_files.py")
    timer = 60
    if module is None:
        publisher.error('Unable to start parsing : module is None')
        return
    directory = config_db.get(module + "|" + "home_dir")
    if directory is not None:
        subprocess.Popen(["python", service_parser, '-n', module,
            '-d', directory, '-t', timer])
        config_db.set(module + "|" + "parsing", 1)
        publisher.info('Parsing of ' + module + 'started.')
    else:
        publisher.error('Unable to start parsing of ' + module + \
                ': home_dir unknown.')
        config_db.set(module + "|" + "parsing", 0)

def manager():
    """
        Manage (start/stop) the process (fetching/parsing) of the modules
    """
    modules = config_db.smembers('modules')
    modules_nr = len(modules)
    # Cleanup
    for module in modules:
        config_db.delete(module + '|parsing')
        config_db.delete(module + '|fetching')

    while True:
        for module in modules:
            parsing = config_db.get(module + "|" + "parsing")
            fetching = config_db.get(module + "|" + "fetching")
            if parsing is None:
                launch_parser(module)
            if fetching is None:
                launch_fetcher(module)

            parsing = config_db.get(module + "|" + "parsing")
            fetching = config_db.get(module + "|" + "fetching")
            if parsing == 0 and fetching == 0:
                config_db.srem('modules', module)

        modules = config_db.smembers('modules')
        if len(modules) != modules_nr:
            modules_nr = len(modules)
            publisher.info('These modules are running: ' + str(modules))
        else:
            time.sleep(sleep_timer)

def stop_services(signum, frame):
    """
        Tell the modules to stop.
    """
    config = ConfigParser.RawConfigParser()
    config_file = "/etc/bgpranking/bgpranking.conf"
    config.read(config_file)
    config_db = redis.Redis(port = int(config.get('redis','port_master')),\
                              db = config.get('redis','config'))
    modules = config_db.smembers('modules')
    # Cleanup
    for module in modules:
        config_db.delete(module + '|parsing')
        config_db.delete(module + '|fetching')
    config_db.delete('modules', modules)
    publisher.info('The services will be stopped ASAP')
    exit(0)

if __name__ == '__main__':
    import signal

    publisher.channel = 'ModuleManager'
    publisher.info('Manager started.')
    signal.signal(signal.SIGHUP, stop_services)
    prepare()
    manager()
