#!/usr/bin/python

"""
Service pushing the routing information. 

This service runs on a file and extract from each RI block the network and the ASN 
announcing this block. Both of them are pushed into the redis database. 


TODO: Extract interesting informations of the bview file, prepare to do a diff 
    egrep -w "^$|PREFIX:|ASPATH:"| awk -F' ' '{print $NF}' |  sed 's/^$/XXXXX/' | tr '\n' ' ' | sed 's/XXXXX/\n/g'| sed 's/^ //' | sort | uniq
"""

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

import redis
routing_db = redis.Redis(db=config.get('redis','routing_redis_db'))

from whois_parser.bgp_parsers import *
import syslog
syslog.openlog('Push_BGP_Routing', syslog.LOG_PID, syslog.LOG_USER)

file = open(sys.argv[1])
entry = ''
for line in file:
    if not line:
        # EOF, quit
        break
    if line == '\n':
        # End of block, extracting the information
        parsed = BGP(entry,  'RIPE')
        if parsed.asn is not None:
            asn = parsed.asn.split()[-1]
            block = parsed.prefix
            if block is not None:
                routing_db.sadd(asn, block)
                routing_db.sadd(block, asn)
            entry = ''
    else :
        # append the line to the current block.
        entry += line
syslog.syslog(syslog.LOG_INFO, sys.argv[1] + ' done')
os.unlink(sys.argv[1])
