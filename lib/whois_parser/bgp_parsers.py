#!/usr/bin/python
# -*- coding: utf-8 -*-
# Original Idea :
# =>  http://code.google.com/p/pywhois/source/browse/trunk/pywhois/parser.py

if __name__ == "__main__":
    import ConfigParser
    config = ConfigParser.RawConfigParser()
    config.read("../../etc/bgp-ranking.conf")
    import sys
    import os
    sys.path.append(os.path.join(config.get('directories','root'),config.get('directories','libraries')))

from abstract_parser import AbstractParser

RIPE_BGP_Dump = {
    'asn'   : 'ASPATH:[\s]*([^\n{]*)', 
    'prefix': 'PREFIX:[\s]*([^\n]*)', 
    'date'  : 'ORIGINATED:[\s]*([^\n]*)'
}

class BGP(AbstractParser):
    possible_regex = {
        'RIPE' : RIPE_BGP_Dump
    }



if __name__ == "__main__":
    import dateutil.parser
    import datetime
    import time
    
    riswhois = "TIME: 06/15/10 08:00:00 \n \
    TYPE: TABLE_DUMP_V2/IPV6_UNICAST\n \
    PREFIX: 2a02::/32\n\
    SEQUENCE: 333737\n\
    FROM: 2001:610:1e08:4::5 AS196613\n\
    ORIGINATED: 06/08/10 07:53:44\n\
    ORIGIN: IGP\n\
    ASPATH: 196613 1125 1103 6939 12684\n\
    MP_REACH_NLRI(IPv6 Unicast)\n\
    NEXT_HOP: ::\n\
    COMMUNITY: 1103:1000"
    ris_whois = BGP(riswhois,  'RIPE')
    print ris_whois.asn
    print ris_whois.prefix
    print time.mktime(dateutil.parser.parse(ris_whois.date).timetuple())


    riswhois = "TIME: 06/15/10 08:00:00 \n \
    TYPE: TABLE_DUMP_V2/IPV6_UNICAST\n \
    PREFIX: 2a02::/32\n\
    SEQUENCE: 333737\n\
    FROM: 2001:610:1e08:4::5 AS196613\n\
    ORIGINATED: 06/08/10 07:53:44\n\
    ORIGIN: IGP\n\
    ASPATH: 196613 1125 1103 6939 12684 {1234,1234}\n\
    MP_REACH_NLRI(IPv6 Unicast)\n\
    NEXT_HOP: ::\n\
    COMMUNITY: 1103:1000"
    ris_whois = BGP(riswhois,  'RIPE')
    print ris_whois.asn
    print ris_whois.prefix
    
    riswhois = "TIME: 06/15/10 07:59:54\n \
    TYPE: TABLE_DUMP_V2/IPV4_UNICAST\n \
    PREFIX: 41.196.34.0/23\n \
    SEQUENCE: 10082\n \
    FROM: 203.119.76.3 AS4608\n \
    ORIGINATED: 05/06/10 01:09:04\n \
    ORIGIN: IGP\n \
    ASPATH: 4608 1221 4637 15412 24863 {37069}\n \
    NEXT_HOP: 203.119.76.3\n \
    AGGREGATOR: AS24863 172.18.1.6\n \""
    ris_whois = BGP(riswhois,  'RIPE')
    print ris_whois.asn
    print ris_whois.prefix
