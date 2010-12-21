import ConfigParser
import sys
import os
config = ConfigParser.RawConfigParser()
config.read("../etc/bgp-ranking.conf")
root_dir =  config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
from ranking.reports import *

import datetime
from graph_generator import GraphGenerator

class MasterControler():

    def __init__(self):
        self.report = Reports()
        self.graph_last_date = datetime.date.today()
        self.graph_first_date = datetime.date.today() - datetime.timedelta(days=30)
        self.report.build_reports()

    def prepare_index(self, source):
        rank = self.report.format_report(source)
        self.histories = []
        for r in rank:
            self.histories.append([r[0], r[1] + 1])

    def get_sources(self):
        self.sources = self.report.sources
    
    def get_as_infos(self, asn = None, source = None):
        if asn is not None:
            self.asn = int(asn)
            as_infos = self.report.get_asn_descs(self.asn, source)
            if as_infos is not None:
                as_graph_infos = self.report.prepare_graphe_js(self.asn, source, self.graph_first_date, self.graph_last_date)
                if as_graph_infos is not None:
                    self.make_graph(as_graph_infos)
        return as_infos
    
    def get_ip_infos(self, asn = None, asn_tstamp = None, source = None):
        if asn is not None and asn_tstamp is not None:
            print asn 
            print asn_tstamp
            return self.report.get_ips_descs(asn, asn_tstamp, source)
    
    def comparator(self, asns = None):
        js_name = config.get('web','canvas_comparator_name')
        if asns is None:
            pass
        else:
            splitted_asns = asns.split()
            g = GraphGenerator(js_name)
            title = ''
            for asn in splitted_asns:
                if asn.isdigit():
                    # as_graph_infos : [ipv4, ipv6, dates, first_date, last_date]
                    as_graph_infos = self.report.prepare_graphe_js(asn)
                    if as_graph_infos is not None:
                        g.add_line(as_graph_infos, str(asn + self.report.ip_key), self.graph_first_date, self.graph_last_date)
                    title += asn + ' '
            if len(g.lines) > 0:
                g.set_title(title)
                g.make_js()
                self.js = g.js
                self.js_name = js_name
            else:
                self.js = self.js_name = None
    
    def make_graph(self, infos):
        js_name = config.get('web','canvas_asn_name')
        g = GraphGenerator(js_name)
        g.add_line(infos, self.report.ip_key, self.graph_first_date, self.graph_last_date )
        g.set_title(self.asn)
        g.make_js()
        self.js = g.js
        self.js_name = js_name
        
