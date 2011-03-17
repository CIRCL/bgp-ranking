#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

    :file:`bin/services/pushing_process.py` - Compute ranking
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Service pushing the routing information. 

    This service runs on a file and extract from each RI block the network and the ASN 
    announcing this block. Both of them are pushed into the redis database. 

"""
import os 
import sys
import ConfigParser
import redis
import syslog

if __name__ == '__main__':
    
    config = ConfigParser.RawConfigParser()
    config_file = "/path/to/bgp-ranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
    from whois_parser.bgp_parsers import *

    routing_db = redis.Redis(port = int(config.get('redis','port_cache')), db=config.get('redis','routing'))

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
