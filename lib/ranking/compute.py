#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Ranking
~~~~~~~

Compute the ranking of a subnet given as parameter
Used in a big loop on each subnet we want to rank.
"""
import ConfigParser

import redis
import IPy

separator = '|'

routing_db = None
global_db = None
history_db = None

# Current key
asn = None
ips_block = None
date = None
source = None

# Current rank
weight = [0.0, 0.0]
rank_by_source = [0.0, 0.0]


def prepare():
    global routing_db
    global global_db
    global history_db
    config = ConfigParser.RawConfigParser()
    config.optionxform = str
    config_file = "/etc/bgpranking/bgpranking.conf"
    config.read(config_file)

    routing_db = redis.Redis(port = int(config.get('redis','port_cache')),\
                                    db = config.get('redis','routing'))
    global_db  = redis.Redis(host=config.get('redis','host_master1'),
                                    port = int(config.get('redis','port_master1')),\
                                    db = config.get('redis','global'))
    history_db = redis.Redis(host=config.get('redis','host_master2'),
                             port = int(config.get('redis','port_master2')),\
                             db = config.get('redis','history'))

def rank_using_key(key):
    """
        The key is the subnet we want to rank
    """
    global asn
    global ips_block
    global date
    global source
    if key is not None:
        asn, ips_block, date, source = key.split(separator)
        ip_count()
        make_index_source()
        rank()
        make_history()

def ip_count():
    """
        Count the number of IPs announced by the ASN (ipv6 and ipv4)
    """
    keys = [str(asn) + '|v4', str(asn) + '|v6']
    ipv4, ipv6 = routing_db.mget(keys)
    if ipv4 is None or ipv6 is None:
        blocks = routing_db.smembers(asn)
        ipv4 = 0
        ipv6 = 0
        for block in blocks:
            ip = IPy.IP(block)
            if ip.version() == 6:
                ipv6 += ip.len()
            else :
                ipv4 += ip.len()
        routing_db.mset({keys[0]: ipv4, keys[1]: ipv6})

def make_index_source():
    """
        Count the number of IPs found in the dataset for this subnet
    """
    global weight
    weight = [0.0, 0.0]
    ips = global_db.smembers('{asn}|{block}|{date}|{source}'.format(asn=asn,
                        block=ips_block, date=date, source=source))
    if len(ips) > 0:
        history_db.srem('{asn}|{date}|clean_set'.format(asn=asn, date=date),
                ips_block)
    for i in ips:
        ip_extract, t = i.split(separator)
        ip = IPy.IP(ip_extract)
        if ip.version() == 4:
            weight[0] += 1.0
        else :
            weight[1] += 1.0

def rank():
    """
        Divide the number of IPs in the datasets by the total announced by the AS
    """
    global rank_by_source
    ipv4, ipv6 = routing_db.mget([str(asn) + '|v4', str(asn) + '|v6'])
    ipv4 = float(ipv4)
    ipv6 = float(ipv6)
    #print weight, ipv4, rank_by_source
    if ipv4 > 0 :
        rank_by_source[0] = float(weight[0]) / ipv4
    if ipv6 > 0 :
        rank_by_source[1] = float(weight[1]) / ipv6

def make_history():
    """
        Save the ranks (by subnets and global) in the database.
    """
    if rank_by_source[0] > 0.0:
        asn_key_v4_details = '{asn}|{date}|{source}|rankv4|details'.format(
                                asn = asn, date = date, source = source)

        history_db.zadd(asn_key_v4_details, **{ips_block: rank_by_source[0]})

        asn_key_v4 = '{asn}|{date}|{source}|rankv4'.format(asn = asn,
                        date = date, source = source)

        temp_rank = history_db.get(asn_key_v4)
        if temp_rank is not None:
            temp_rank = float(temp_rank) + rank_by_source[0]
        else:
            temp_rank = rank_by_source[0]
        history_db.set(asn_key_v4, temp_rank)

    if rank_by_source[1] > 0.0:
        asn_key_v6_details = '{asn}|{date}|{source}|rankv6|details'.format(
                                asn = asn, date = date, source = source)

        history_db.zadd(asn_key_v6_details, **{ips_block: rank_by_source[1]})

        asn_key_v6 = '{asn}|{date}|{source}|rankv6'.format(asn = asn,
                        date = date, source = source)

        temp_rank = history_db.get(asn_key_v6)
        if temp_rank is not None:
            temp_rank = float(temp_rank) + rank_by_source[1]
        else:
            temp_rank = rank_by_source[1]
        history_db.set(asn_key_v6, temp_rank)
