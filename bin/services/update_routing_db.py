#!/usr/bin/python
import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('global','root')
sleep_timer = int(config.get('global','sleep_timer'))
sys.path.append(os.path.join(root_dir,config.get('global','lib')))

import syslog
syslog.openlog('BGP_Routing_Update', syslog.LOG_PID, syslog.LOG_USER)
from whois_parser.bgp_parsers import *

import time
import redis
import dateutil.parser
#time.mktime(dateutil.parser.parse(ris_whois.date).timetuple())

"""
Update the routing Database
"""

def usage():
    print "update_routing_db.py source"
    exit (1)

if len(sys.argv) < 2:
    usage()

source = sys.argv[1]

key = config.get('redis','key_temp_routing')
temp_db = redis.Redis(db=config.get('redis','temp_reris_db'))
routing_db = redis.Redis(db=config.get('redis','routing_redis_db'))


while 1:
    entry = temp_db.lpop(key)
    if entry == None :
        time.sleep(sleep_timer)
        syslog.syslog(syslog.LOG_INFO, 'Waiting')
        continue
    parsed = BGP(entry,  source)
    asn = parsed.asn.split()[-1]
    block = parsed.prefix
#    old_asn = routing_db.get(block)
#    if old_asn != None:
#        if old_asn == asn:
#            old_time = routing_db.get(block + ':date')
#            if int(old_time) < int(time):
#                routing_db.set(block, asn)
#                routing_db.set(block + ':date', time)
#            continue
#        routing_db.srem(old_asn, block)
#        print('Removing ' + block +' of ' +  old_asn)
    routing_db.sadd(asn, block)
    routing_db.sadd(block, asn)
