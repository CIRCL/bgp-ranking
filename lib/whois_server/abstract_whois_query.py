#!/usr/bin/python

import redis
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")

class WhoisQuery():
    
    def __init__(self):
        self.redis_whois_server = redis.Redis(db=int(config.get('whois_server','redis_db')) )
    
    def append_value(self, key):
        to_return = '\n'
        key_value = self.redis_whois_server.get(key)
        if not key_value:
            to_return += key + ' not found ! (incomplete whois db)'
        else:
            to_return += key_value
        return to_return

    def get_value(self, flag, query):
        to_return = ''
        key = self.redis_whois_server.get(query + ':' + flag)
        if key:
            to_return += self.append_value(key)
        return to_return

    def get_value_set(self, flag, query):
        to_return = ''
        keys = self.redis_whois_server.get(query + ':' + flag)
        if keys:
            keys = keys.split()
            for key in keys:
                to_return += self.append_value(key)
        return to_return
