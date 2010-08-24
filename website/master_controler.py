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

    def __init__(self, date = datetime.datetime.now()):
        self.report = Reports(date)

    def prepare_index(self, source = None, limit = 50):
        self.report.best_of_day(limit, source)
        self.index_table = self.report.histories
    
    def get_sources(self):
        self.report.get_sources()
        self.sources = self.report.sources
    
    def get_as_infos(self, asn = None, source = None):
        self.asn = int(asn)
        self.report.get_asn_descs(self.asn, source)
        self.as_infos = self.report.asn_descs_to_print
        as_graph_infos = self.report.graph_infos
        if as_graph_infos is not None:
            self.make_graph(as_graph_infos)
    
    def get_ip_infos(self, asn_desc = None, source = None):
        self.report.get_ips_descs(asn_desc, source)
        self.ip_infos = self.report.ip_descs_to_print
    
    #FIXME: what if len(labels) != len(line)
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
                    self.report.prepare_graphe_js(asn)
                    # as_graph_infos : [ipv4, ipv6, dates, first_date, last_date]
                    as_graph_infos = self.report.graph_infos
                    g.add_line([as_graph_infos[0], as_graph_infos[2]], asn + ' IPv4', as_graph_infos[3], as_graph_infos[4] )
                    g.add_line([as_graph_infos[1], as_graph_infos[2]], asn + ' IPv6', as_graph_infos[3], as_graph_infos[4] )
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
        g.add_line(infos[0], 'IPv4')
        g.add_line(infos[1], 'IPv6')
        g.set_labels(infos[2])
        g.set_title(self.asn)
        g.make_js()
        self.js = g.js
        self.js_name = js_name
        
