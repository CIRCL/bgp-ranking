#!/bin/python
# -*- coding: utf-8 -*-


import redis

global_db = redis.Redis(port=6379, db=5)

r = redis.Redis(unix_socket_path='./redis_export.sock')

while True:
    asn_ts= r.spop('asn_ts')
    asn, ts = asn_ts.split('|')
    if asn_ts is None:
        break
    keys = [asn_ts + '|ips_block', asn_ts + '|timestamp']
    block, description = global_db.mget(keys)
    p = global_db.pipeline(False)
    p.hset(asn + '|' + block, ts, description)
    p.sadd(asn, block)
    p.delete(*keys)
    p.srem(asn, ts)
    p.execute()

