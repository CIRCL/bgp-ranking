#!/usr/bin/python
# Needs redis-py from git! the stable version has a bug in keys()

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('global','root')

import redis 

redis_whois_server = redis.Redis(db=int(config.get('whois_server','redis_db')) )

import IPy

#def usage():
#    print "arin_query.py query"
#    exit(1)
#
#if len(sys.argv) < 2:
#    usage()

#query = sys.argv[1]
#ip = None
#try:
#    ip = IPy.IP(query).int()
#except:
#    pass

#if ip:
#    print(whois_ip(ip))
#else:
#   print(whois_asn(query))

def whois_asn(query):
    to_return = redis_whois_server.get(query)
    if not to_return:
        to_return = 'ASN not found.'
    else:
        to_return += get_value('orgid', query)
        to_return += get_value_set('pocs', query)
    return to_return

def append_value(key):
    to_return = '\n'
    key_value = redis_whois_server.get(key)
    if not key_value:
        to_return += key + ' not found ! (incomplete whois db)'
    else:
        to_return += key_value
    return to_return

def get_value(flag, query):
    to_return = ''
    key = redis_whois_server.get(query + ':' + flag)
    if key:
        to_return += append_value(key)
    return to_return

def get_value_set(flag, query):
    to_return = ''
    keys = redis_whois_server.get(query + ':' + flag)
    if keys:
        keys = keys.split()
        for key in keys:
            to_return += append_value(key)
    return to_return

def find_key(ip_int):
    to_return = redis_whois_server.get(ip_int)
    if not to_return:
        prec = ip_int-1
        key_prec = None
        next = ip_int+1
        key_next = None
        while key_prec == None:
            key_prec = redis_whois_server.get(prec)
            prec -=1
        while key_next == None:
            key_next = redis_whois_server.get(next)
            next+=1
        if key_prec == key_next:
            to_return = key_prec
        else:
            to_return = None
    return to_return

def whois_ip(ip_int):
    key = find_key(ip_int)
    to_return = ''
    if not key:
        to_return += 'IP not found.'
    else:
        to_return += redis_whois_server.get(key)
        to_return += get_value('orgid', key)
        to_return += get_value('parent', key)
        to_return += get_value_set('pocs', key)
    return to_return
