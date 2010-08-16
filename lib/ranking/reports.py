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
    
    def filter_query_source(self, query, limit):
        entries = query.count()
        histories = {}
        first = 0 
        last = limit
        while limit > 0:
            select = query[first:last]
            for s in select:
                if histories.get(s.asn, None) is None:
                    histories[s.asn] = [s.timestamp, s.asn, s.rankv4]
                    limit -= 1
                    if limit <= 0:
                        break
            first = last
            last = last + limit
            if first > entries:
                break
        return histories

    #FIXME: query on IPv6
    #FIXME: the code is just ugly... 
    def best_of_day(self, limit = 50, source = None):
        global_query = True
        histo = {}
        if source is not None and len(source) >0 :
            s = Sources.query.get(unicode(source))
            if s is not None:
                query = History.query.filter(and_(History.source == s, and_(History.rankv4 > 0.0, and_(History.timestamp <= self.date, History.timestamp >= self.date - datetime.timedelta(days=1))))).order_by(desc(History.timestamp))
                histo = filter_query_source(query, limit)
                global_query = False
        if global_query:
            histo = {}
            for s in Sources.query.all():
                query = History.query.filter(and_(History.source == s, and_(History.rankv4 > 0.0, and_(History.timestamp <= self.date, History.timestamp >= self.date - datetime.timedelta(days=1))))).order_by(desc(History.timestamp))
                h_temp = filter_query_source(query, limit)
                if len(histo) == 0:
                    histo = h_temp
                else:
                    for t in h_temp:
                        if histo.get(t[1], None):
                            histo[t[1]] = t
                        else:
                            histo[t.asn][2] += t[2]
        for h in histo:
            self.histories.append(h)
        self.histories.sort(key=lambda x:x[2], reverse=True )

    def prepare_graphe_js(self,  asn):
        histories = History.query.filter_by(asn=int(asn)).order_by(desc(History.timestamp)).all()
        date = None
        tmptable = []
        for history in histories:
            prec_date = date
            date = history.timestamp.date()
            if date != prec_date:
                tmptable.append([str(history.timestamp.date()), float(history.rankv4), float(history.rankv6)] )
        dates = []
        ipv4 = []
        ipv6 = []
        for t in reversed(tmptable):
            dates.append(t[0])
            ipv4.append(t[1])
            ipv6.append(t[2])
        self.graph_infos = [ipv4, ipv6, dates]

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
                self.asn_descs_to_print.append([desc.id, desc.timestamp, desc.owner, desc.ips_block, nb_of_ips])

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
