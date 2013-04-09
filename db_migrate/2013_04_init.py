#!/bin/python
# -*- coding: utf-8 -*-

import redis
import bgpranking

date = bgpranking.get_default_date()
dates_sources = bgpranking.prepare_sources_by_dates(date, 1000)
asns = bgpranking.existing_asns_timeframe(dates_sources)

r = redis.Redis(unix_socket_path='./redis_export.sock')

for asn in asns:
    timestamps = bgpranking.get_all_asn_timestamps(asn)
    p = r.pipeline(False)
    for ts in timestamps:
        p.sadd('asn_ts', "{asn}|{ts}".format(asn=asn, ts=ts))
    p.execute()
