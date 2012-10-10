#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

    :file:`bin/services/ris.py` - Push RIS Entries
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Insert the RIS Whois information in the database.
    Link the entries with their ASN.

    A new asn "object" is created by :meth:`add_asn_entry` if it does not already exists
"""

import ConfigParser
import time

from pubsublogger import publisher

import redis

# Temporary, until the parsers are a system library
import sys
sys.path.append('../../lib/')
from whois_parser.whois_parsers import Whois

import datetime

import dateutil.parser

separator = '|'
default_asn = -1
default_asn_descr = 'Default AS, none found using RIS Whois.'
default_asn_route = '0.0.0.0/0'
default_asn_key = None

key_asn = 'asn'
key_owner = 'owner'
key_ips_block = 'ips_block'

index_asns_details = 'asns_details'
index_asns= 'asns'

temp_ris = 'ris'
temp_no_asn = 'no_asn'

stop_ris = 'stop_ris'

cache_db = None
cache_db_0 = None
global_db = None
config_db = None

default_asn_desc = None
max_consecutive_errors = 5
sleep_timer = 10

def prepare():
    """
        Connection to the redis instances
    """
    global cache_db
    global cache_db_0
    global global_db
    global config_db
    global default_asn_key
    config = ConfigParser.RawConfigParser()
    config_file = "/etc/bgpranking/bgpranking.conf"
    config.read(config_file)
    separator = config.get('input_keys','separator')

    cache_db = redis.Redis(port = int(config.get('redis','port_cache')),
                        db = int(config.get('redis','cache_ris')))
    cache_db_0 = redis.Redis(port = int(config.get('redis','port_cache')),
                        db = int(config.get('redis','temp')))
    global_db = redis.Redis(port = int(config.get('redis','port_master')),
                        db = int(config.get('redis','global')))
    config_db = redis.Redis(port = int(config.get('redis','port_master')),
                        db = config.get('redis','config'))
    config_db.delete(stop_ris)

    default_asn_members = global_db.smembers(default_asn)
    if len(default_asn_members) == 0 :
        default_asn_key = add_asn_entry(default_asn, default_asn_descr,
                default_asn_route)
    else:
        default_asn_key = '{asn}{sep}{tstamp}'.format(\
                asn=default_asn, sep = separator,
                tstamp=default_asn_members.pop())

def add_asn_entry(asn, owner, ips_block):
    """
        Add a new subnet to the ASNs known by the system,
        only if the subnet is not already present. Elsewhere, simply return
        the value from the database.
    """
    key = None
    asn_timestamps = global_db.smembers(asn)
    key_list = [ "{asn}{sep}{timestamp}{sep}{ips_block}".format(\
                    asn = asn, timestamp = asn_timestamp,
                    sep = separator, ips_block = key_ips_block)
                 for asn_timestamp in asn_timestamps ]
    known_asn_ips_blocks = []
    if len(key_list) != 0:
        known_asn_ips_blocks = global_db.mget(key_list)
    i = 0
    for block in known_asn_ips_blocks:
        if block == ips_block:
            asn, timestamp, b = key_list[i].split(separator)
            temp_key = "{asn}{sep}{timestamp}".format(asn=asn,
                    sep = separator, timestamp=timestamp)
            if global_db.get("{key}{sep}{owner}".format(key = temp_key,
                sep = separator, owner = key_owner)) == owner:
                key = temp_key
                break
        i +=1
    if key is None:
        lock = global_db.getset('locked_new_ans', 1)
        if lock == 1 :
            # ensure the same new entry is not inserted twice
            return None
        timestamp = datetime.datetime.utcnow().isoformat()
        key = "{asn}{sep}{timestamp}".format(asn=asn, sep = separator,
                timestamp=timestamp)
        to_set = {\
                    "{key}{sep}{owner}".format(\
                                key = key, sep = separator,
                                owner = key_owner) : owner,
                    "{key}{sep}{ips_block}".format(\
                                key = key, sep = separator,
                                ips_block = key_ips_block): ips_block
                 }
        pipeline = global_db.pipeline(False)
        pipeline.sadd(asn, timestamp)
        pipeline.mset(to_set)
        pipeline.set('locked_new_ans', 0)
        pipeline.execute()
        publisher.info('New asn entry inserted in the database: {asn}, {owner}, {ipblock}'\
                .format(asn = asn, owner = owner, ipblock = ips_block))
    return key

def update_db_ris(data):
    """
        Use :meth:`add_asn_entry` to update the database with the RIS
        whois informations from :class:`WhoisFetcher` and return the
        corresponding entry.
    """
    splitted = data.partition('\n')
    ris_origin = splitted[0]
    riswhois = splitted[2]
    ris_whois = Whois(riswhois,  ris_origin)
    if not ris_whois.origin:
        return default_asn_key
    else:
        return add_asn_entry(ris_whois.origin, ris_whois.description,
                ris_whois.route)

def get_ris():
    """
        Get the RIS whois information if the IPs without ASNs and put
        it into redis.
        The entry has now a link with his ASN.
    """
    while True:
        card_no_asn = cache_db_0.scard(temp_no_asn)
        if card_no_asn != 0:
            for ip_set in cache_db_0.smembers(temp_no_asn):
                errors = 0
                ip_set_card = cache_db_0.scard(ip_set)
                if ip_set_card == 0:
                    cache_db_0.srem(temp_no_asn, ip_set)
                    continue
                for i in range(ip_set_card):
                    ip_details = cache_db_0.spop(ip_set)
                    if ip_details is None:
                        break
                    a, b, source, c = ip_set.split(separator)
                    ip, timestamp = ip_details.split(separator)
                    entry = cache_db.get(ip)
                    if entry is None:
                        errors += 1
                        cache_db_0.sadd(ip_set, ip_details)
                        if errors >= max_consecutive_errors:
                            cache_db_0.sadd(temp_ris, ip)
                    else:
                        errors = 0
                        asn = update_db_ris(entry)
                        if asn is None:
                            # Concurrency conflict, retry later
                            cache_db_0.sadd(ip_set, ip_details)
                            continue
                        date = dateutil.parser.parse(timestamp).date().isoformat()
                        index_day_asns_details = '{date}{sep}{source}{sep}{key}'\
                                .format(sep=separator, date=date,
                                        source=source, key=index_asns_details)
                        index_day_asns = '{date}{sep}{source}{sep}{key}'\
                                .format(sep = separator, date=date,
                                        source=source, key=index_asns)
                        index_as_ips = '{asn}{sep}{date}{sep}{source}'\
                                .format(sep = separator, asn = asn, date=date,
                                        source=source)
                        if global_db.sismember(index_as_ips, ip_details) is False:
                            pipeline = global_db.pipeline(False)
                            pipeline.sadd(index_day_asns_details, asn)
                            pipeline.sadd(index_day_asns, asn.split(separator)[0])
                            pipeline.sadd(index_as_ips, ip_details)
                            pipeline.execute()
                    if i%100 == 0 and config_db.exists(stop_ris):
                        break
                    if i%100000 == 0:
                        publisher.info('{card} RIS Whois to insert from {ip_set}'\
                                .format(card = cache_db_0.scard(ip_set),
                                    ip_set = ip_set))
        time.sleep(sleep_timer)
        if config_db.exists(stop_ris):
            publisher.info('RISWhoisInsert stopped.')
            break

def stop_services(signum, frame):
    """
        Set a value in redis to quit the loop properly
    """
    config = ConfigParser.RawConfigParser()
    config_file = "/etc/bgpranking/bgpranking.conf"
    config.read(config_file)
    config_db = redis.Redis(port = int(config.get('redis','port_master')),
            db = config.get('redis','config'))
    config_db.set(stop_ris, 1)

if __name__ == '__main__':
    import signal

    publisher.channel = 'RISWhoisInsert'
    publisher.info('RISWhoisInsert started.')
    signal.signal(signal.SIGHUP, stop_services)
    prepare()
    get_ris()
