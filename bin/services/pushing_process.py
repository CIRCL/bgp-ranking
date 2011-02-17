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
config_file = "/mnt/data/gits/bgp-ranking/etc/bgp-ranking.conf"
config.read(config_file)
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

import redis
routing_db = redis.Redis(db=config.get('redis','routing'))

from whois_parser.bgp_parsers import *
import syslog
syslog.openlog('Push_BGP_Routing', syslog.LOG_PID, syslog.LOG_USER)

file = open(sys.argv[1])
entry = ''
pipeline = routing_db.pipeline()
i = 0 
for line in file:
    if not line:
        # EOF, quit
        break
    if line == '\n':
        i += 1 
        # End of block, extracting the information
        parsed = BGP(entry,  'RIPE')
        if parsed.asn is not None:
            asn = parsed.asn.split()[-1]
            block = parsed.prefix
            if block is not None:
                pipeline.sadd(asn, block)
#                routing_db.sadd(block, asn)
            entry = ''
        if i >= 10000:
            pipeline.execute()
            pipeline = routing_db.pipeline()
            i = 0 
    else :
        # append the line to the current block.
        entry += line
pipeline.execute()
syslog.syslog(syslog.LOG_INFO, sys.argv[1] + ' done')
os.unlink(sys.argv[1])
