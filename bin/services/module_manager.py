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
import syslog
import time
import redis


def usage():
    print "module_manager.py"
    exit (1)

class ModuleManager(object):

    def __init__(self):
        config = ConfigParser.RawConfigParser()
        config_file = "/path/to/bgp-ranking.conf"
        config.read(config_file)
        root_dir = config.get('directories','root')
        services_dir = os.path.join(root_dir,config.get('directories','services'))
        sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

        self.config_db = redis.Redis(port = int(config.get('redis','port_master')),\
                                       db = config.get('redis','config'))
        self.service_fetcher = os.path.join(services_dir, "fetch_raw_files.py")
        self.service_parser = os.path.join(services_dir, "parse_raw_files.py")
        syslog.openlog('BGP_Ranking_Module_Manager', syslog.LOG_PID, syslog.LOG_LOCAL5)
        self.sleep_timer = int(config.get('sleep_timers','short'))


    def launch_fetcher(self, module):
        if module is None:
            syslog.syslog(syslog.LOG_ERR, 'Unable to start fetching : module is None')

        url = self.config_db.get(module + "|" + "url")
        if url is None:
            syslog.syslog(syslog.LOG_INFO, module + ' does not have an URL, no fetcher.')
            self.config_db.set(module + "|" + "fetching", 0)

        directory = self.config_db.get(module + "|" + "home_dir")
        if directory is not None:
            subprocess.Popen(["python", self.service_fetcher, module, directory, url])
            self.config_db.set(module + "|" + "fetching", 1)
            syslog.syslog(syslog.LOG_INFO, 'Fetching of ' + module + 'started.')
        else:
            syslog.syslog(syslog.LOG_ERR, 'Unable to start fetching of ' + module + ': home_dir unknown.')
            self.config_db.set(module + "|" + "fetching", 0)


    def launch_parser(self, module):
        if module is None:
            syslog.syslog(syslog.LOG_ERR, 'Unable to start parsing : module is None')

        directory = self.config_db.get(module + "|" + "home_dir")
        if directory is not None:
            subprocess.Popen(["python", self.service_parser, module, directory])
            self.config_db.set(module + "|" + "parsing", 1)
            syslog.syslog(syslog.LOG_INFO, 'Parsing of ' + module + 'started.')
        else:
            syslog.syslog(syslog.LOG_ERR, 'Unable to start parsing of ' + module + ': home_dir unknown.')
            self.config_db.set(module + "|" + "parsing", 0)

    def get_config_db(self):
        return self.config_db

    def manager(self):
        modules = self.config_db.smembers('modules')
        modules_nr = len(modules)
        while True:
            for module in modules:
                parsing = self.config_db.get(module + "|" + "parsing")
                fetching = self.config_db.get(module + "|" + "fetching")
                if parsing is None:
                    self.launch_parser(module)
                if fetching is None:
                    self.launch_fetcher(module)

                parsing = self.config_db.get(module + "|" + "parsing")
                fetching = self.config_db.get(module + "|" + "fetching")
                if parsing == 0 and fetching == 0:
                    self.config_db.srem('modules', module)

            modules = config_db.smembers('modules')
            if len(modules) != modules_nr:
                modules_nr = len(modules)
                syslog.syslog(syslog.LOG_INFO, 'These modules are running: ' + str(modules))
            else:
                time.sleep(self.sleep_timer)

def stop_services():
    config = ConfigParser.RawConfigParser()
    config_file = "/path/to/bgp-ranking.conf"
    config.read(config_file)
    config_db = redis.Redis(port = int(config.get('redis','port_master')),\
                              db = config.get('redis','config'))
    modules = config_db.smembers('modules')
    for module in modules:
        config_db.set(module + "|" + "parsing", 0)
        config_db.set(module + "|" + "fetching", 0)
    syslog.syslog(syslog.LOG_INFO, 'The services will be stopped ASAP')

if __name__ == '__main__':
    import signal
    syslog.openlog('BGP_Ranking_Module_Manager', syslog.LOG_PID, syslog.LOG_LOCAL5)
    syslog.syslog(syslog.LOG_INFO, 'Manager started.')
    mm = ModuleManager()
    config_db = mm.get_config_db()
    signal.signal(signal.SIGHUP, stop_services)
    mm.manager()
