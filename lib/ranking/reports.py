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


items = config.items('modules_to_parse')

from sqlalchemy import and_, desc

class Reports():
    
    def __init__(self, date = datetime.datetime.now()):
        self.date = date
        self.impacts = {}
        for item in items:
            self.impacts[item[0]] = int(item[1])
    
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
                    if s.source_source is not None:
                        histories[s.asn] = [s.timestamp, s.asn, s.rankv4 * float(self.impacts[str(s.source_source)]) + 1.0]
                    else:
                        histories[s.asn] = [s.timestamp, s.asn, s.rankv4 + 1.0]
                    limit -= 1
                    if limit <= 0:
                        break
            first = last
            last = last + limit
            if first > entries:
                break
        return histories
    
    def get_source_entry(self, source):
        if source is not None:
            return Sources.query.get(unicode(source))
        else:
            return None

    #FIXME: query on IPv6
    def best_of_day(self, limit = 50, source = None):
        global_query = True
        histo = {}
        s = self.get_source_entry(source)
        if s is not None:
            query = History.query.filter(and_(History.source == s, and_(History.rankv4 > 0.0, and_(History.timestamp <= self.date, History.timestamp >= self.date - datetime.timedelta(days=1))))).order_by(desc(History.rankv4), desc(History.timestamp))
            histo = self.filter_query_source(query, limit)
            global_query = False
        if global_query:
            histo = {}
            for s in Sources.query.all():
                query = History.query.filter(and_(History.source == s, and_(History.rankv4 > 0.0, and_(History.timestamp <= self.date, History.timestamp >= self.date - datetime.timedelta(days=1))))).order_by(desc(History.rankv4), desc(History.timestamp))
                h_temp = self.filter_query_source(query, limit)
                if len(histo) == 0:
                    histo = h_temp
                else:
                    for t, h in h_temp.items():
                        if histo.get(h[1], None) is None:
                            histo[h[1]] = h
                        else:
                            histo[h[1]][2] += h[2]
        self.histories = []
        for t, h in histo.items():
            self.histories.append(h)
        self.histories.sort(key=lambda x:x[2], reverse=True )

    def prepare_graphe_js(self,  asn, source = None):
        s = self.get_source_entry(source)
        if s is not None:
            query = History.query.filter(and_(History.source == s, asn == int(asn))).order_by(desc(History.timestamp))
        else : 
            query = History.query.filter(asn == int(asn)).order_by(desc(History.timestamp))
        histories = query.all()
        date = None
        tmptable = []
        for history in histories:
            prec_date = date
            date = history.timestamp.date()
            if date != prec_date:
                if history.source_source is not None:
                    tmptable.append([str(history.timestamp.date()), float(history.rankv4) * float(self.impacts[str(history.source_source)]) + 1.0 , float(history.rankv6)* float(self.impacts[str(history.source_source)]) + 1.0] )
                else:
                    tmptable.append([str(history.timestamp.date()), float(history.rankv4) + 1.0 , float(history.rankv6) + 1.0] )
        dates = []
        ipv4 = []
        ipv6 = []
        for t in reversed(tmptable):
            dates.append(t[0])
            ipv4.append(t[1])
            ipv6.append(t[2])
        self.graph_infos = [ipv4, ipv6, dates]

    def get_asn_descs(self, asn, source = None):
        self.prepare_graphe_js(asn)
        asn_db = ASNs.query.filter_by(asn=int(asn)).first()
        if asn_db is not None:
            asn_descs = ASNsDescriptions.query.filter(ASNsDescriptions.asn==asn_db).all()
        else:
            asn_descs = None
        self.asn_descs_to_print = None
        s = self.get_source_entry(source)
        if s is not None:
            query = IPsDescriptions.query.filter(and_(History.source == s, and_(IPsDescriptions.asn == desc, and_(IPsDescriptions.timestamp <= self.date, IPsDescriptions.timestamp >= self.date - datetime.timedelta(days=1)))))
        else:
            query = IPsDescriptions.query.filter(and_(IPsDescriptions.asn == desc, and_(IPsDescriptions.timestamp <= self.date, IPsDescriptions.timestamp >= self.date - datetime.timedelta(days=1))))
        if asn_descs is not None:
            self.asn_descs_to_print = []
            for desc in asn_descs:
                nb_of_ips = query.count()
                self.asn_descs_to_print.append([desc.id, desc.timestamp, desc.owner, desc.ips_block, nb_of_ips])

    def get_ips_descs(self, asn_desc_id, source = None):
        asn_desc = ASNsDescriptions.query.filter_by(id=int(asn_desc_id)).first()
        if asn_desc is not None:
            s = self.get_source_entry(source)
            if s is not None:
                query = IPsDescriptions.query.filter(and_(History.source == s, and_(IPsDescriptions.asn == asn_desc, and_(IPsDescriptions.timestamp <= self.date, IPsDescriptions.timestamp >= self.date - datetime.timedelta(days=1)))))
            else : 
                query = IPsDescriptions.query.filter(and_(IPsDescriptions.asn == asn_desc, and_(IPsDescriptions.timestamp <= self.date, IPsDescriptions.timestamp >= self.date - datetime.timedelta(days=1))))
            ip_descs = query.all()
        else:
            ip_descs = None
        self.ip_descs_to_print = None
        if ip_descs is not None:
            self.ip_descs_to_print = []
            for desc in ip_descs:
                self.ip_descs_to_print.append([desc.timestamp, desc.ip_ip, desc.list_name, desc.infection, desc.raw_informations, desc.whois])
