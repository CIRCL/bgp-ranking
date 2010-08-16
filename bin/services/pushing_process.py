#!/usr/bin/python
import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))


routing_db = redis.Redis(db=config.get('redis','routing_redis_db'))

from whois_parser.bgp_parsers import *
import syslog
syslog.openlog('Push_BGP_Routing', syslog.LOG_PID, syslog.LOG_USER)

file = open(fname)
entry = ''
for line in file:
    if not line:
        break
    if line == '\n':
        parsed = BGP(entry,  'RIPE')
        if parsed.asn is not None:
            asn = parsed.asn.split()[-1]
            block = parsed.prefix
            if block is not None:
                routing_db.sadd(asn, block)
                routing_db.sadd(block, asn)
            entry = ''
    else :
        entry += line
syslog.syslog(syslog.LOG_INFO, fname + ' done')
os.unlink(fname)
