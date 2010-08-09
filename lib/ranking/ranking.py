#!/usr/bin/python

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.optionxform = str
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

import syslog
syslog.openlog('Ranking', syslog.LOG_PID, syslog.LOG_USER)
from whois_parser.bgp_parsers import *

from db_models.ranking import *
from db_models.voting import *
from sqlalchemy import and_

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
    
    def rank_and_save(self, date = datetime.datetime.now()):
        self.date = date
        self.old_entry = False
        if self.date > datetime.date.today():
            self.old_entry = True
        self.ip_count()
        self.make_index()
        self.rank()
        self.make_history()

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
        ips = []
        # weight['source'] = [ipv4, ipv6]
        self.weight = {}
        for desc in descs:
            ips += IPsDescriptions.query.filter(and_(IPsDescriptions.asn == desc, and_(IPsDescriptions.timestamp <= self.date, IPsDescriptions.timestamp >= self.date - datetime.timedelta(days=1)))).all()
            """
            SELECT * FROM `IPsDescriptions` WHERE `IPsDescriptions`.asn_id = desc AND `IPsDescriptions`.timestamp <= date AND `IPsDescriptions`.timestamp >= date - datetime.timedelta(days=1)
            """
        for i in ips:
            ip = IPy.IP(i.ip_ip)
            if self.weight.get(str(i.list_name), None) is None:
                self.weight[str(i.list_name)] = [0, 0]
            if ip.version() == 6:
                self.weight[str(i.list_name)][1] += impacts[str(i.list_name)]
            else :
                self.weight[str(i.list_name)][0] += impacts[str(i.list_name)]

    def rank(self):
        self.rank_by_source = {}
        print self.weight
        for key in self.weight:
            self.rank_by_source[key] = [0.0, 0.0]
            if self.ipv4 > 0 :
                self.rank_by_source[key][0] = (float(self.weight[key][0])/self.ipv4)
            elif self.ipv6 > 0 :
                self.rank_by_source[key][1] = (float(self.weight[key][1])/self.ipv6)
    
    def make_history(self):
        votes = Votes.query.filter_by(asn=int(self.asn)).all()
        for key in self.rank_by_source:
            s = Sources.query.get(unicode(key))
            if s is None:
                s = Sources(source = unicode(key))
            history = History(asn=int(self.asn), rankv4=self.rank_by_source[key][0], rankv6=self.rank_by_source[key][1], vote = votes, source = s)
        if self.old_entry:
            history.timestamp = self.date
        v_session = VotingSession()
        v_session.commit()
        v_session.close()

class MetaRanking():
    def make_ranking_all_asns(self, date = datetime.date.today()):
        asns = ASNs.query.all()
        for asn in asns:
            r = Ranking(asn.asn)
            r.rank_and_save(date)

    def list_dates(self, first_date, last_date):
        list = []
        number_of_days = (last_date + datetime.timedelta(days=1) - first_date).days
        for day in range(number_of_days):
            list += first_date + datetime.timedelta(days=day)
        return list
    
    def make_ranking_all_asns_interval(self, first_date, last_date = datetime.date.today()):
        dates = list_dates(first_date, last_date)
        for date in dates:
            make_ranking_all_asns(date)
    
    


if __name__ == "__main__":
    import datetime
    import dateutil.parser
#    r = Ranking(42473)
#    r.ip_count()
#    print(r.ipv4, r.ipv6)
#    r.make_index(dateutil.parser.parse('2010-06-25'))
#    print(r.weightv4, r.weightv6)
#    r.rank()
#    print('Rank v4:' + str(r.rankv4))
#    print('Rank v6:' + str(r.rankv6))
#    r.make_history()
    mr = MetaRanking()
    mr.make_ranking_all_asns()
    v_session = VotingSession()
    v_session.commit()
    v_session.close()
    
