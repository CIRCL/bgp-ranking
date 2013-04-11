#!/bin/python
# -*- coding: utf-8 -*-

import redis
import bgpranking

r = redis.Redis(unix_socket_path='./redis_export.sock')
date = bgpranking.get_default_date()
dates_sources = bgpranking.prepare_sources_by_dates(date, 1)

p = r.pipeline(False)
for date, sources in dates_sources.iteritems():
    keys = ['{date}|{source}|asns_details'.format(date=date, source=s)
            for s in sources]
    print keys
    if len(keys) > 0:
        p.sadd('asns_details', *keys)
p.execute()

asns = bgpranking.existing_asns_timeframe(dates_sources)

for asn in asns:
    timestamps = bgpranking.get_all_asn_timestamps(asn)
    p = r.pipeline(False)
    for ts in timestamps:
        p.sadd('asn_ts', "{asn}|{ts}".format(asn=asn, ts=ts))
    p.execute()
