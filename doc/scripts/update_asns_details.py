#!/usr/bin/python

import redis
import datetime

r_history = redis.Redis(db=6)
r_global = redis.Redis(db=5)

# format day : YYYY-MM-DD
def update_day(day):
    sources = r_global.smembers('{day}|sources'.format(day = day))
    if len(sources) > 0 :
        asns_details = {}
        for source in sources:
            asns_details[source] = r_global.smembers('{day}|{source}|asns_details'.format(day = day, source = source))
        to_drop = []
        pipeline = r_history.pipeline()
        for source, details in asns_details.iteritems():
            for detail in details:
                asn, timestamp = detail.split('|')
                current = '{detail}|{day}|{source}|rankv4'.format(detail = detail, day = day, source = source)
                rank = r_history.get(current)
                if rank is not None:
                    to_drop.append(current)
                    asn_key_v4_details = '{asn}|{day}|{source}|rankv4|details'.format(asn = asn, day = day, source = source)
                    pipeline.zadd(asn_key_v4_details, **{timestamp: rank})

                current = '{detail}|{day}|{source}|rankv6'.format(detail = detail, day = day, source = source)
                rank = r_history.get(current)
                if rank is not None:
                    to_drop.append(current)
                    asn_key_v6_details = '{asn}|{day}|{source}|rankv6|details'.format(asn = asn, day = day, source = source)
                    pipeline.zadd(asn_key_v6_details, **{timestamp: rank})
        pipeline.execute()
        if len(to_drop) > 0:
            r_history.delete(*to_drop)


def make_days(first_date, last_date):
    dates = []
    current = first_date
    while current <= last_date:
        dates.append(current.strftime("%Y-%m-%d"))
        current += datetime.timedelta(days=1)
    return dates

def convert_all():
    graph_last_date = datetime.date.today()
    graph_first_date = datetime.date.today() - datetime.timedelta(days=60)
    dates = make_days(graph_first_date, graph_last_date)
    for date in dates:
        update_day(date)

def recompute_ranks_day(day):
    sources = r_global.smembers('{day}|sources'.format(day = day))
    if len(sources) > 0 :
        asns = {}
        for source in sources:
            asns[source] = r_global.smembers('{day}|{source}|asns'.format(day = day, source = source))
        pipeline = r_history.pipeline()
        for source, asns in asns.iteritems():
            for asn in asns:
                details_zset = r_history.zrange('{asn}|{day}|{source}|rankv4|details'.format(asn = asn, day = day, source = source), 0, -1, withscores = True)
                asn_rank = 0.0
                for detail in details_zset:
                    asn_rank += float(detail[1])
                pipeline.set('{asn}|{day}|{source}|rankv4'.format(asn = asn, day = day, source = source), asn_rank)

                details_zset = r_history.zrange('{asn}|{day}|{source}|rankv6|details'.format(asn = asn, day = day, source = source), 0, -1, withscores = True)
                asn_rank = 0.0
                for detail in details_zset:
                    asn_rank += float(detail[1])
                pipeline.set('{asn}|{day}|{source}|rankv6'.format(asn = asn, day = day, source = source), asn_rank)
        pipeline.execute()


def recompute_all_ranks():
    graph_last_date = datetime.date.today()
    graph_first_date = datetime.date.today() - datetime.timedelta(days=60)
    dates = make_days(graph_first_date, graph_last_date)
    for date in dates:
        recompute_ranks_day(date)

def delete_useless_old_keys():
    graph_last_date = datetime.date.today()
    graph_first_date = datetime.date.today() - datetime.timedelta(days=60)
    dates = make_days(graph_first_date, graph_last_date)
    for date in dates:
        keys = r_history.keys("*|*|" + date + "|*|*")
        if len(keys) > 0:
            r_history.delete(*keys)
