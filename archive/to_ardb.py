#!/usr/bin/env python
# -*- coding: utf-8 -*-

from redis import StrictRedis
import socket
from dateutil.parser import parse
from datetime import date, timedelta


def perdelta(start, end, delta):
    curr = start
    while curr <= end:
        yield curr
        curr += delta


def simple_check_ipblock(detail_key, asn_block, block, quiet=False):
    valid = True
    splitted = block.split('/')
    if len(splitted) != 2:
        print(detail_key, 'has invalid content (ip block invalid):', asn_block)
        return False
    ip, mask = splitted
    if not mask.isdigit():
        print(detail_key, 'has invalid content (IP block mask invalid):', asn_block)
        valid = False
    try:
        socket.inet_aton(ip)
    except:
        try:
            socket.inet_pton(socket.AF_INET6, ip)
        except:
            print(detail_key, 'has invalid content (IP of block invalid):', asn_block)
            valid = False
    return valid


def copy_valid_blocks(src, dst):
    p = src.pipeline(False)
    [p.smembers(a) for a in range(0, 400000)]
    blocks = p.execute()
    asn_blocks = zip(range(0, 400000), blocks)
    for a, known_blocks in asn_blocks:
        to_copy = []
        for block in known_blocks:
            if '/' not in block and ':' in block:
                continue
            to_copy.append(block)
            blockdescr = src.hgetall('{}|{}'.format(a, block))
            p = dst.pipeline(False)
            [p.hset('{}|{}'.format(a, block), ts, descr) for ts, descr in blockdescr.items()]
            p.execute()
        if to_copy:
            dst.sadd(a, *to_copy)


def copy_all_ips(src, dst, year, move=False):
    for day in perdelta(date(year, 1, 1), date(year, 12, 31), timedelta(days=1)):
        sources = src.smembers('{}|sources'.format(day))
        if sources:
            print(day)
            dst.sadd('{}|sources'.format(day), *sources)
            if move:
                src.delete('{}|sources'.format(day))
        else:
            print('No data for', day)
            continue
        for s in sources:
            dst_pipeline = dst.pipeline(False)
            asns = src.smembers('{}|{}|asns'.format(day, s))
            if asns:
                dst_pipeline.sadd('{}|{}|asns'.format(day, s), *asns)
                if move:
                    src.delete('{}|{}|asns'.format(day, s))
            asns_d = src.smembers('{}|{}|asns_details'.format(day, s))
            if asns_d:
                dst_pipeline.sadd('{}|{}|asns_details'.format(day, s), *asns_d)
                if move:
                    src.delete('{}|{}|asns_details'.format(day, s))
            else:
                continue
            details_keys = ['{}|{}|{}'.format(detail, day, s) for detail in asns_d]
            p_details = src.pipeline(False)
            [p_details.smembers(k) for k in details_keys]
            contents = p_details.execute()
            all_content = zip(details_keys, contents)
            [dst_pipeline.sadd(k, *content) for k, content in all_content if content]
            if move:
                src.delete(*details_keys)
            dst_pipeline.execute()


def check_asns(src, alreadychecked_blocks):
    p = src.pipeline(False)
    [p.smembers(a) for a in range(0, 400000)]
    blocks = p.execute()
    asn_blocks = zip(range(0, 400000), blocks)
    for a, known_blocks in asn_blocks:
        for block in known_blocks:
            if '/' not in block and ':' in block:
                print(a, 'has invalid content (ip block invalid):', block)
                continue
            if not simple_check_ipblock(a, block, block):
                continue
            blockdescr_key = '{}|{}'.format(a, block)
            if blockdescr_key in alreadychecked_blocks:
                continue
            alreadychecked_blocks.append(blockdescr_key)
            blockdescr = src.hgetall(blockdescr_key)
            for ts, descr in blockdescr.items():
                try:
                    parse(ts)
                except:
                    print(blockdescr_key, 'has invalid content (date invalid):', ts, descr)


def check_raw_data(src, date, alreadychecked_asn, alreadychecked_blocks):
    sources = src.smembers('{}|sources'.format(date))
    for s in sources:
        asns_key = '{}|{}|asns'.format(date, s)
        asns = src.smembers(asns_key)
        for a in asns:
            if a in alreadychecked_asn:
                continue
            alreadychecked_asn.append(a)
            if not a.isdigit():
                print(asns_key, 'contains invalid ASN:', a)
                continue
            known_blocks = src.smembers(a)
            for block in known_blocks:
                if not simple_check_ipblock(a, block, block):
                    continue
                blockdescr_key = '{}|{}'.format(a, block)
                if blockdescr_key in alreadychecked_blocks:
                    continue
                alreadychecked_blocks.append(blockdescr_key)
                blockdescr = src.hgetall(blockdescr_key)
                for ts, descr in blockdescr.items():
                    try:
                        parse(ts)
                    except:
                        print(blockdescr_key, 'has invalid content (date invalid):', ts, descr)

        detail_key = '{}_details'.format(asns_key)
        details = src.smembers(detail_key)
        for asn_block in details:
            splitted = asn_block.split('|')
            if len(splitted) != 2:
                print(detail_key, 'has invalid content:', asn_block)
                continue
            asn, block = splitted
            if not asn.isdigit() and asn != '-1':
                print(detail_key, 'has invalid content (ASN not a number):', asn_block)
            simple_check_ipblock(detail_key, asn_block, block)
            allips_key = '{}|{}|{}'.format(asn_block, date, s)
            all_ips = src.smembers(allips_key)
            for ip_ts in all_ips:
                splitted = ip_ts.split('|')
                if len(splitted) != 2:
                    print(allips_key, 'has invalid content:', ip_ts)
                    continue
                ip, date = splitted
                try:
                    socket.inet_aton(ip)
                except:
                    print(allips_key, 'has invalid content (IP invalid):', ip_ts)
                try:
                    parse(date)
                except:
                    print(allips_key, 'has invalid content (date invalid):', ip_ts)


def check_data(src):
    alreadychecked_asn = ['-1']
    alreadychecked_blocks = ['-1|0.0.0.0/0']

    check_asns(src, dst)

    for day in perdelta(date(2014, 1, 1), date(2014, 1, 31), timedelta(days=1)):
        check_raw_data(src, day, alreadychecked_asn, alreadychecked_blocks)


if __name__ == '__main__':
    src = StrictRedis(host='149.13.33.71', port='6379', db=5, decode_responses=True)
    dst = StrictRedis(host='127.0.0.1', port='16379', decode_responses=True)
    copy_all_ips(src, dst, 2015, move=True)
