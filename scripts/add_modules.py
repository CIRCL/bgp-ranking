#!/usr/bin/python
# -*- coding: utf-8 -*-


import ConfigParser
import redis

class AddModules(object):
    def __init__(self):
        self.config_file = "/path/to/bgp-ranking.conf"

        config = ConfigParser.SafeConfigParser()
        config.read(self.config_file)

        self.config_db  = redis.Redis(unix_socket_path = self.config.get('redis','unix_socket'),\
                                        db = int(config.get('redis','config')))

    def push_module_information(self, module, impact, home_dir = None, url = None):
        self.config_db.set(module, impact)
        if home_dir is not None:
            self.config_db.set(module + "|" + "home_dir", home_dir)
        if url is not None:
            self.config_db.set(module + "|" + "url", url)

        # !!! Always last !!!!
        self.config_db.sadd('modules', module)

        response = raw_input("Do you want to start a new process for " + module + "? (y/N) ")
        if response == 'y':
            self.config_db.delete(module + "|" + "parsing")
            self.config_db.delete(module + "|" + "fetching")

    def from_config_file(self):
        config_file_redis = self.config_file + ".redis"
        redis_config = ConfigParser.RawConfigParser()
        redis_config.optionxform = str
        redis_config.read(config_file_redis)
        items = redis_config.items('modules')
        for module, params in items:
            p = params.split()
            add_modules.push_module_information(module, *p)

if __name__ == '__main__':

    add_modules = AddModules()
    response = raw_input("Do you want to import modules from the config file ? (y/N) ")
    if response == 'y':
        add_modules.from_config_file()
    response = None
    
    while True:
        response = raw_input("Do you want to import a new module? (y/N) ")
        if response == 'y':
            classname = raw_input("ClassName? (required)")
            impact = raw_input("Impact? (required, float)")
            home_dir = raw_input("Home directory? (required)")
            url = raw_input("URL? (optional)")
            add_modules.push_module_information(classname, impact, home_dir, url)
        else:
            break

    print("Do not forget to add the module in lib/modules/ !")
