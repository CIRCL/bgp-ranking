#!/usr/bin/python
# -*- coding: utf-8 -*-


import ConfigParser
import redis


config_file = "/path/to/bgp-ranking.conf"
redis_config_file = config_file + ".redis"

config = ConfigParser.SafeConfigParser()
config.read(config_file)

config_db  = redis.Redis( port = int(self.config.get('redis','port_master')),\
                            db = int(self.config.get('redis','config')))

redis_config = ConfigParser.SafeConfigParser()
redis_config.read(redis_config_file)

p = config_db.pipeline()

items = config.items('modules_to_parse')
for source, weight in items:
    p.set(source, weight)

p.execute()
