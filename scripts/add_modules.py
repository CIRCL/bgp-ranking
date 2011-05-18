#!/usr/bin/python
# -*- coding: utf-8 -*-


import ConfigParser
import redis

class AddModules(object):
    def __init__(self):
        config_file = "/path/to/bgp-ranking.conf"
        config_file_redis = config_file + ".redis"

        config = ConfigParser.SafeConfigParser()
        config.read(config_file)

        self.config_db  = redis.Redis( port = int(config.get('redis','port_master')),\
                                    db = int(config.get('redis','config')))

    def push_module_information(self, module, impact, home_dir = None, url = None):
        self.config_db.set(module, impact)
        if home_dir is not None:
            self.config_db.set(module + "|" + "home_dir", home_dir)
        if url is not None:
            self.config_db.set(module + "|" + "url", home_dir)

        # !!! Always last !!!!
        self.config_db.sadd('modules', name)

if __name__ == '__main__':
    # Make it a "ncurse interface"
    config_file = "/path/to/bgp-ranking.conf"
    config_file_redis = config_file + ".redis"

    redis_config = ConfigParser.RawConfigParser()
    redis_config.optionxform = str
    redis_config.read(config_file_redis)

    add_modules = AddModules()

    items = redis_config.items('modules')
    for module, params in items:
        p = params.split()
        add_modules.push_module_information(module, *p)
