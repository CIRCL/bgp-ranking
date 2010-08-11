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
            pass

    def prepare_index(self, source = None, limit = 50, date = datetime.datetime.now()):
        self.report = Reports(date)
        self.report.best_of_day(limit, source)
        self.index_table = self.report.histories
    
    def get_sources(self):
        self.report.get_sources()
        self.sources = self.report.sources
    
    def get_as_infos(self, asn = None):
        self.asn = int(asn)
        self.report.get_asn_descs(self.asn)
        self.as_infos = self.report.asn_descs_to_print
        as_graph_infos = self.report.graph_infos
        self.make_graph(as_graph_infos)
    
    def get_ip_infos(self, asn_desc = None):
        self.report.get_ips_descs(asn_desc)
        self.ip_infos = self.report.ip_descs_to_print
    
    #FIXME: what is len(labels) != len(line)
    def comparator(self, asns, js_name = 'comparator'):
        splitted_asns = asns.split()
        g = GraphGenerator(js_name)
        g.set_title(asns)
        for asn in splitted_asns:
            self.report.prepare_graphe_js(asn)
            as_graph_infos = self.report.graph_infos
            g.add_line(as_graph_infos[0], asn + ' IPv4')
            g.add_line(as_graph_infos[1], asn + ' IPv6')
            g.set_labels(as_graph_infos[2])
        g.make_js()
        self.js = g.js
        self.js_name = js_name
    
    def make_graph(self, infos, js_name = 'rank'):
        g = GraphGenerator(js_name)
        g.add_line(infos[0], 'IPv4')
        g.add_line(infos[1], 'IPv6')
        g.set_labels(infos[2])
        g.set_title(self.asn)
        g.make_js()
        self.js = g.js
        self.js_name = js_name
        
