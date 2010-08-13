#!/usr/bin/python

import sys
import IPy
config = ConfigParser.RawConfigParser()
config.read("../etc/bgp-ranking.conf")
root_dir =  config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
from ranking.compute import *

from db_models.ranking import *

import redis

routing_db = redis.Redis(db=config.get('redis','routing_redis_db'))

items = config.items('modules_to_parse')

import syslog
syslog.openlog('Compute_Ranking_Process', syslog.LOG_PID, syslog.LOG_USER)

interval = sys.argv[1].split()
first = int(interval[0])
last = int(interval[1])

asns = ASNs.query.all()[first:last]
syslog.syslog(syslog.LOG_INFO, 'Computing rank of ' + str(len(asns)) + ' ASNs: ' + str(first) + ' ' + str(last))
for asn in asns:
    r = Ranking(asn.asn)
    r.rank_and_save(date)
    pass
syslog.syslog(syslog.LOG_INFO, 'Computing rank of ' + str(first) + ' ' + str(last) + ' is done.')


