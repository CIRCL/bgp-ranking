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
        max = History.query.filter(and_(History.rankv4 > 1.0, and_(History.timestamp <= self.date, History.timestamp >= self.date - datetime.timedelta(days=1)))).order_by(desc(History.rankv4), History.timestamp).count()
        asns = []
        self.histories = []
        first = 0 
        last = limit
        while limit > 0:
            select = History.query.filter(and_(History.rankv4 > 1.0, and_(History.timestamp <= self.date, History.timestamp >= self.date - datetime.timedelta(days=1)))).order_by(desc(History.rankv4), History.timestamp)[first:last]
            for s in select:
                if s.asn not in asns:
                    asns.append(s.asn)
                    self.histories.append(s)
                    limit -= 1
            first = last
            last = last + limit
            if first > max:
                break
    
    def get_votes(self, history):
        if history.votes is not None:
            temp_votes = history.votes.split(';')
            self.votes = []
            for vote in temp_votes:
                vote_splitted = vote.split(':')
                user = Users.query.get_by(id=vote_splitted[0])
                self.votes.append([user, vote_splitted[1]])

    def prepare_graphes_js(self,  asn):
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
        
        self.script = """window.onload = function
{
    line2 = new RGraph.Line('myCanvas2', """ + str(ipv4) + """);
    line2.Set('chart.hmargin', 10);
    line2.Set('chart.labels', """  + str(dates) +  """);
    line2.Set('chart.linewidth', 3);
    line2.Set('chart.shadow', true);
    line2.Set('chart.shadow.offsetx', 2);
    line2.Set('chart.shadow.offsety', 2);
    line2.Set('chart.ymax', 65);
    line2.Set('chart.units.post', 'l');
    line2.Set('chart.gutter', 35);
    line2.Set('chart.noxaxis', true);
    line2.Set('chart.noendxtick', true);
    line2.Set('chart.title', 'An example of axes both sides');
    line2.Draw();

    line3 = new RGraph.Line('myCanvas2', """ + str(ipv6) + """);
    line3.Set('chart.hmargin', 10);
    line3.Set('chart.linewidth', 3);
    line3.Set('chart.shadow', true);
    line3.Set('chart.shadow.offsetx', 2);
    line3.Set('chart.shadow.offsety', 2);
    line3.Set('chart.yaxispos', 'right');
    line3.Set('chart.noendxtick', true);
    line3.Set('chart.background.grid', false);
    line3.Set('chart.ymax', 65);
    line3.Set('chart.colors', ['blue', 'red']);
    line3.Set('chart.units.pre', '$');
    line3.Set('chart.gutter', 35);
    line3.Set('chart.key', ['Cost', 'Volume']);
    line3.Set('chart.key.background', 'rgba(255,255,255,0.5)');
    line3.Draw();
}"""

    

    def get_asn_descs(self, asn):
        asn_db = ASNs.query.filter_by(asn=int(asn)).first()
        if asn_db is not None:
            self.asn_descs = ASNsDescriptions.query.filter(ASNsDescriptions.asn==asn_db).all()
            return True
        self.asn_descs = None
        return False

    def get_ips_descs(self, asn_desc_id):
        asn_desc = ASNsDescriptions.query.filter_by(id=int(asn_desc_id)).first()
        if asn_desc is not None:
            self.ip_descs = IPsDescriptions.query.filter(and_(IPsDescriptions.asn == asn_desc, and_(IPsDescriptions.timestamp <= self.date, IPsDescriptions.timestamp >= self.date - datetime.timedelta(days=1)))).all()
            return True
        self.ip_descs = None
        return False
