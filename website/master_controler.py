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

        # Ensure there is something to display
        self.report = Reports(datetime.date.today())
        self.report.flush_temp_db()
        self.report.build_reports_lasts_days(int(self.config.get('ranking','days')))
        self.report.build_reports()
        self.set_params()
        

    def set_params(self, date = None):
        """
            Set the params to always display the latest version of the rankings
        """
        self.graph_last_date = datetime.date.today()
        self.graph_first_date = datetime.date.today() - datetime.timedelta(days=30)
        if date is None:
            date = self.graph_last_date
        if self.report is not None:
            self.report.set_sources(date)
        self.report.set_dates()
        self.report.set_date(date)


    def prepare_index(self, source, date = None):
        """
            Get the data from the model and prepare the ranks to pass to the index
        """
        self.set_params(date)
        rank = self.report.format_report(source = source, date = date)
        histories = []
        if rank is not None:
            for r in rank:
                histories.append([r[0], r[1] + 1, r[2]])
        return histories

    def get_sources(self):
        """
            Returns all the available sources given by the model
        """
        self.sources = self.report.sources

    def get_dates(self):
        """
            Returns all the available dates given by the model
        """
        self.dates = self.report.dates
    
    def get_as_infos(self, asn = None, source = None, date = None):
        """
            Get the data needed to display the page of the details on an AS 
        """
        as_infos, current_sources = [], []
        if asn is not None:
            self.set_params(date)
            as_infos, current_sources = self.report.get_asn_descs(asn, source, date)
            if len(as_infos) == 0:
                return [], []
            as_graph_infos, self.sources = self.report.prepare_graphe_js(asn, self.graph_first_date, self.graph_last_date, source)
            self.make_graph(asn, as_graph_infos)
        return as_infos, current_sources
    
    def get_ip_infos(self, asn = None, asn_tstamp = None, source = None, date = None):
        """
            Get the descriptions of the IPs of a subnet
        """
        if asn is not None and asn_tstamp is not None:
            self.set_params(date)
            return self.report.get_ips_descs(asn, asn_tstamp, source, date)
    
    def comparator(self, asns = None):
        """
            Get the data needed to display the page of the comparator
        """
        js_name = self.config.get('web','canvas_comparator_name')
        asns_to_return = []
        if asns is not None:
            self.set_params()
            splitted_asns = asns.split()
            g = GraphGenerator(js_name)
            title = ''
            for asn in splitted_asns:
                if asn.isdigit():
                    asns_to_return.append(asn)
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
        return " ".join(asns_to_return)
    
    def make_graph(self, asn, infos):
        """
            Generate the graph with the data provided by the model
        """
        js_name = self.config.get('web','canvas_asn_name')
        g = GraphGenerator(js_name)
        g.add_line(infos, self.report.ip_key, self.graph_first_date, self.graph_last_date )
        g.set_title(asn)
        g.make_js()
        self.js = g.js
        self.js_name = js_name
        
