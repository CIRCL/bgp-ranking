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
    
    def __init__(self, date = datetime.datetime.now()):
        self.date = date
    
    def get_sources(self):
        self.sources = []
        for s in Sources.query.all():
            self.sources.append(s.source)

    #FIXME: query on IPv6
    def best_of_day(self, limit = 50, source = None):
        global_query = True
        if source is not None and len(source) >0 :
            s = Sources.query.get(unicode(source))
            if s is not None:
                query = History.query.filter(and_(History.source == s, and_(History.rankv4 > 0.0, and_(History.timestamp <= self.date, History.timestamp >= self.date - datetime.timedelta(days=1))))).order_by(desc(History.rankv4), History.timestamp)
                global_query = False
        if global_query:
            query = History.query.filter(and_(History.rankv4 > 0.0, and_(History.timestamp <= self.date, History.timestamp >= self.date - datetime.timedelta(days=1)))).order_by(desc(History.rankv4), History.timestamp)
        entries = query.count()
        self.histories = {}
        first = 0 
        last = limit
        while limit > 0:
            select = query[first:last]
            for s in select:
                h_temp = self.histories.get(s.asn, None)
                if h_temp is None:
                    self.histories[s.asn] = [s.timestamp, s.asn, s.rankv4]
                    self.histories.append(s)
                    limit -= 1
                elif h_temp.source != s.source:
                    self.histories[s.asn][2] += s.rankv4
            first = last
            last = last + limit
            if first > entries:
                break

    def prepare_graphe_js(self,  asn):
        histories = History.query.filter_by(asn=int(asn)).order_by(desc(History.timestamp)).all()
        date = None
        tmptable = []
        for history in histories:
            prec_date = date
            date = history.timestamp.date()
            if date != prec_date:
                tmptable.append([str(history.timestamp.date()), str(history.rankv4), str(history.rankv6)] )
        dates = []
        ipv4 = []
        ipv6 = []
        for t in reversed(tmptable):
            dates.append(t[0])
            ipv4.append(t[1])
            ipv6.append(t[2])
        self.graph_infos = [str(ipv4), str(ipv6), str(dates), max(max(ipv4),max(ipv6))]

    def get_asn_descs(self, asn):
        self.prepare_graphe_js(asn)
        asn_db = ASNs.query.filter_by(asn=int(asn)).first()
        if asn_db is not None:
            asn_descs = ASNsDescriptions.query.filter(ASNsDescriptions.asn==asn_db).all()
        else:
            asn_descs = None
        self.asn_descs_to_print = None
        if asn_descs is not None:
            self.asn_descs_to_print = []
            for desc in asn_descs:
                nb_of_ips = IPsDescriptions.query.filter(and_(IPsDescriptions.asn == desc, and_(IPsDescriptions.timestamp <= self.date, IPsDescriptions.timestamp >= self.date - datetime.timedelta(days=1)))).count()
                self.asn_descs_to_print.append([desc.id, desc.timestamp, desc.owner, desc.block, nb_of_ips])

    def get_ips_descs(self, asn_desc_id):
        asn_desc = ASNsDescriptions.query.filter_by(id=int(asn_desc_id)).first()
        if asn_desc is not None:
            ip_descs = IPsDescriptions.query.filter(and_(IPsDescriptions.asn == asn_desc, and_(IPsDescriptions.timestamp <= self.date, IPsDescriptions.timestamp >= self.date - datetime.timedelta(days=1)))).all()
        else:
            ip_descs = None
        self.ip_descs_to_print = None
        if ip_descs is not None:
            self.ip_descs_to_print = []
            for desc in ip_descs:
                self.ip_descs_to_print.append([desc.timestamp, desc.ip_ip, desc.list_name, desc.infection, desc.raw_informations, desc.whois])
