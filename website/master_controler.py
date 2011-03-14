# -*- coding: utf-8 -*-
"""
    Controler class of the website
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The website respects the MVC pattern and this class is the controler.
    It gets the datas from the `report` class.

"""

import ConfigParser
import sys
import os

import datetime
from graph_generator import GraphGenerator

class MasterControler():

    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        config_file = "/path/to/bgp-ranking.conf"
        self.config.read(config_file)
        root_dir =  self.config.get('directories','root')
        sys.path.append(os.path.join(root_dir,self.config.get('directories','libraries')))
        from ranking.reports import Reports
        
        self.graph_last_date = datetime.date.today()
        self.graph_first_date = datetime.date.today() - datetime.timedelta(days=30)
        self.report = Reports(self.graph_last_date)
        self.report.build_reports()

    def prepare_index(self, source):
        """
            Get the data from the model and prepare the ranks to pass to the index
        """
        rank = self.report.format_report(source)
        self.histories = []
        for r in rank:
            self.histories.append([r[0], r[1] + 1])

    def get_sources(self):
        """
            Returns all the available sources given by the model
        """
        self.sources = self.report.sources
    
    def get_as_infos(self, asn = None, source = None):
        """
            Get the data needed to display the page of the details on an AS 
        """
        if asn is not None:
            self.asn = int(asn)
            as_infos = self.report.get_asn_descs(self.asn, source)
            as_graph_infos, self.sources = self.report.prepare_graphe_js(self.asn, self.graph_first_date, self.graph_last_date, source)
            self.make_graph(as_graph_infos)
        return as_infos
    
    def get_ip_infos(self, asn = None, asn_tstamp = None, source = None):
        """
            Get the descriptions of the IPs of a subnet
        """
        if asn is not None and asn_tstamp is not None:
            return self.report.get_ips_descs(asn, asn_tstamp, source)
    
    def comparator(self, asns = None):
        """
            Get the data needed to display the page of the comparator
        """
        js_name = self.config.get('web','canvas_comparator_name')
        if asns is None:
            pass
        else:
            splitted_asns = asns.split()
            g = GraphGenerator(js_name)
            title = ''
            for asn in splitted_asns:
                if asn.isdigit():
                    as_graph_infos, self.sources = self.report.prepare_graphe_js(asn, self.graph_first_date, self.graph_last_date)
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
        """
            Generate the graph with the data provided by the model
        """
        js_name = self.config.get('web','canvas_asn_name')
        g = GraphGenerator(js_name)
        g.add_line(infos, self.report.ip_key, self.graph_first_date, self.graph_last_date )
        g.set_title(self.asn)
        g.make_js()
        self.js = g.js
        self.js_name = js_name
        
