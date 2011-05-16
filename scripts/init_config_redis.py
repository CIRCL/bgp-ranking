#!/usr/bin/python
# -*- coding: utf-8 -*-


import ConfigParser
import redis


config_file = "/path/to/bgp-ranking.conf"
config_file_redis = config_file + ".redis"

config = ConfigParser.SafeConfigParser()
config.read(config_file)

config_db  = redis.Redis( port = int(config.get('redis','port_master')),\
                            db = int(config.get('redis','config')))

redis_config = ConfigParser.RawConfigParser()
redis_config.optionxform = str
redis_config.read(config_file_redis)

p = config_db.pipeline()

items = redis_config.items('modules_to_parse')
for source, weight in items:
    p.set(source, weight)

p.execute()
