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


items = redis_config.items('modules')
for dummy_name, modules_names in items:
    names = modules_names.split()
    for name in names:
        p.sadd('modules', name)

items = redis_config.items('modules_impacts')
for source, weight in items:
    p.set(source, weight)

items = redis_config.items('modules_home_dirs')
for source, home_dir in items:
    p.set(source + "|" + "home_dir", home_dir)

items = redis_config.items('modules_urls')
for source, url in items:
    p.set(source + "|" + "url", url)


p.execute()
