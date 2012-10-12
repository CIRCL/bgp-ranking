#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
    Entry point of the API
"""

import helper_global as h


def get_asn_informations(asn):
    to_return = {}
    timestamps = h.global_db.smembers(asn)
    if len(timestamps) == 0:
        to_return['return_code'] = 0
        to_return['return_vebose'] = 'Unknown ASN'
        return to_return
    key_tmpl = '{asn}|{date}|{source}|rankv4'
    keys = []
    for date, sources in h.sources_by_dates.iteritems():
        keys += [key_tmpl.format(asn = asn, date = date,
            source = source) for source in sources]
    ranks = h.history_db.mget(keys)
    if set(ranks) == set([None]):
        to_return['return_code'] = 0
        to_return['return_vebose'] = 'No rankings in this timeframe.'
        return to_return
    i = 0
    data = {}

    for date, sources in h.sources_by_dates.iteritems():
        data[date] = {}
        data[date]['details'] = []
        data[date]['total'] = 0
        for source in sources:
            if ranks[i] is None:
                ranks[i] = 0
            data[date]['details'].append((source, float(ranks[i])))
            data[date]['total'] += float(ranks[i])
            i += 1
    to_return['return_code'] = 1
    to_return['return_vebose'] = 'Got ranks.'
    to_return['data'] = data
    return to_return


if __name__ == '__main__':
    h.prepare()
    print get_asn_informations(43674)
