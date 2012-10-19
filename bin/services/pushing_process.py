#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

    :file:`bin/services/pushing_process.py` - Push RIS
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Service pushing the routing information.

    This service runs on a file and extract from each RI block the network and the ASN
    announcing this block. Both of them are pushed into the redis database.

"""
import os
import sys
import ConfigParser
import redis

from pubsublogger import publisher
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Parse a bview file.')
    parser.add_argument("-f", "--filename", required=True, type=str, help='Name of the file.')
    args = parser.parse_args()

    filename = args.filename

    config = ConfigParser.RawConfigParser()
    config_file = "/etc/bgpranking/bgpranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories',
        'libraries')))
    from whois_parser.bgp_parsers import BGP

    routing_db = redis.Redis(port = int(config.get('redis','port_cache')),
            db=config.get('redis','routing'))

    publisher.channel = 'Ranking'

    file = open(filename)
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
                    pipeline.sadd('asns', asn)
                entry = ''
            if i%10000 == 0:
                pipeline.execute()
                pipeline = routing_db.pipeline()
        else :
            # append the line to the current block.
            entry += line
    pipeline.execute()
    publisher.info('{f} finished, {nb} entries impported.'.\
            format(f=filename, nb = i))
    os.unlink(filename)
