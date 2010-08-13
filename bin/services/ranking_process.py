#!/usr/bin/python

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.optionxform = str
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

from db_models.ranking import *
from ranking.compute import *

import redis

routing_db = redis.Redis(db=config.get('redis','routing_redis_db'))

items = config.items('modules_to_parse')

import syslog
syslog.openlog('Compute_Ranking_Process', syslog.LOG_PID, syslog.LOG_USER)

interval = sys.argv[1].split()

asns = ASNs.query.all()[interval[0]:interval[1]]
syslog.syslog(syslog.LOG_INFO, 'Computing rank of ' + str(len(asns)) + ' ASNs: ' + str(interval))
for asn in asns:
#    r = Ranking(asn.asn)
#    r.rank_and_save(date)
    pass
syslog.syslog(syslog.LOG_INFO, 'Computing rank of ' + str(interval) + ' is done.')


v_session = VotingSession()
v_session.commit()
v_session.close()
