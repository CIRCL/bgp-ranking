#!/usr/bin/python

"""
Very small script used to computer the number of IPs announced by a particular ASN 
"""

import os
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.optionxform = str
config_file = "/mnt/data/gits/bgp-ranking/etc/bgp-ranking.conf"
config.read(config_file)
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

import redis
import IPy
routing_db = redis.Redis(db=config.get('redis','routing'))



def usage():
    print "./number_of_IPs.py <ASN>"
    exit (1)

if len(sys.argv) < 2:
    usage()

asn = sys.argv[1]

def ip_count(asn):
    keyv4 = str(asn) + ':v4'
    keyv6 = str(asn) + ':v6'
    ipv4 = routing_db.get(keyv4)
    ipv6 = routing_db.get(keyv6)
    if ipv4 is None:
        blocks = routing_db.smembers(asn)
        ipv4 = 0
        ipv6 = 0
        for block in blocks:
            ip = IPy.IP(block)
            if ip.version() == 6:
                ipv6 += ip.len()
            else :
                ipv4 += ip.len()
        routing_db.set(keyv4, ipv4)
        routing_db.set(keyv6, ipv6)
    else:
        ipv4 = int(ipv4)
        ipv6 = int(ipv6)
    return ipv4, ipv6

ipv4, ipv6 = ip_count(asn)

print(asn + " announce " + str(ipv4) + " IPv4")
print(asn + " announce " + str(ipv6) + " IPv6")

