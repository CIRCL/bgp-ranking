#!/usr/bin/python

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.optionxform = str
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('global','root')
sleep_timer = int(config.get('global','sleep_timer'))
sys.path.append(os.path.join(root_dir,config.get('global','lib')))

import syslog
syslog.openlog('Ranking', syslog.LOG_PID, syslog.LOG_USER)
from whois_parser.bgp_parsers import *

from db_models.ranking import *

import time
import redis
import IPy

routing_db = redis.Redis(db=config.get('redis','routing_redis_db'))

items = config.items('modules_to_parse')
impacts = {}
for item in items:
    impacts[item[0]] = int(item[1])


class Ranking():
    
    def __init__(self, asn):
        self.asn = asn 

    def ip_count(self):
        blocks = routing_db.smembers(self.asn)
        self.ipv4 = 0
        self.ipv6 = 0
        for block in blocks:
            ip = IPy.IP(block)
            if ip.version() == 6:
                self.ipv6 += ip.len()
            else :
                self.ipv4 += ip.len()

    def make_index(self):
        descs = ASNsDescriptions.query.filter_by(asn=ASNs.query.filter_by(asn=self.asn).first()).all()
        print descs
        ips = []
        self.weightv4 = 0
        self.weightv6 = 0
        for desc in descs:
            ips += IPsDescriptions.query.filter_by(asn = desc).all()
        ipv4 = 0
        ipv6 = 0
        for i in ips:
            ip = IPy.IP(i.ip_ip)
            if ip.version() == 6:
                ipv6 += 1
                self.weightv6 += impacts[str(i.list_name)]
            else :
                ipv4 += 1
                self.weightv4 += impacts[str(i.list_name)]

    def rank(self):
        self.rankv4 = 1
        self.rankv6 = 1
        if self.ipv4 > 0 :
            self.rankv4 += (self.weightv4/self.ipv4)
        if self.ipv6 > 0 :
            self.rankv6 += (self.weightv6/self.ipv6)


if __name__ == "__main__":
    import datetime
    r = Ranking(12684)
    r.ip_count()
    print(r.ipv4, r.ipv6)
    r.make_index()
    print(r.weightv4, r.weightv6)
    r.rank()
    print('Rank v4:' + str(r.rankv4))
    print('Rank v6:' + str(r.rankv6))
    
