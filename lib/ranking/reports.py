#!/usr/bin/python

if __name__ == "__main__":
    import os 
    import sys
    import ConfigParser
    config = ConfigParser.RawConfigParser()
    config.optionxform = str
    config.read("../../etc/bgp-ranking.conf")
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
    
from db_models.ranking import *
from db_models.voting import *


from sqlalchemy import and_, desc

class Reports():
    histories = None
    asn_descs = None
    ip_descs = None
    
    def __init__(self, date = datetime.datetime.now()):
        self.date = date

    def best_of_day(self, limit = 50):
        self.histories = History.query.filter(and_(History.rankv4 > 1.0, and_(History.timestamp <= self.date, History.timestamp >= self.date - datetime.timedelta(days=1)))).order_by(desc(History.rankv4))[0:limit]
    
    def get_votes(self, history):
        if history.votes is not None:
            temp_votes = history.votes.split(';')
            self.votes = []
            for vote in temp_votes:
                vote_splitted = vote.split(':')
                user = Users.query.get_by(id=vote_splitted[0])
                self.votes.append([user, vote_splitted[1]])

    def get_asn_descs(self, asn):
        asn_db = ASNs.query.filter_by(asn=int(asn)).first()
        self.asn_descs = ASNsDescriptions.query.filter(and_(ASNsDescriptions.asn==asn_db, and_(History.timestamp <= self.date, History.timestamp >= self.date - datetime.timedelta(days=1)))).all()

    def get_ips_descs(self, asn_desc_id):
        asn_desc = ASNsDescriptions.query.filter_by(id=int(asn_desc_id)).first()
        self.ip_descs = IPsDescriptions.query.filter(and_(IPsDescriptions.asn == asn_desc, and_(History.timestamp <= self.date, History.timestamp >= self.date - datetime.timedelta(days=1)))).all()
