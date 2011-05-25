# -*- coding: utf-8 -*-
"""
    Controler class of the website
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    The website respects the MVC design pattern and this class is the controler.
    It gets the datas from the `report` class.

"""

import ConfigParser
import sys
import os

import datetime
from graph_generator import GraphGenerator

class MasterControler(object):

    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        config_file = "/path/to/bgp-ranking.conf"
        self.config.read(config_file)
        root_dir =  self.config.get('directories','root')
        sys.path.append(os.path.join(root_dir,self.config.get('directories','libraries')))
        from ranking.reports import Reports

        # Ensure there is something to display
        self.report = Reports()
        self.report.flush_temp_db()
        self.report.build_reports_lasts_days(int(self.config.get('ranking','days')))
        self.report.build_last_reports()
        self.days_graph = 30

    def prepare_index(self, source, date):
        """
            Get the data from the model and prepare the ranks to pass to the index
        """
        rank = self.report.format_report(source, date)
        if rank is not None:
            return [ [r[0], 1 + r[1], ', '.join(r[2])] for r in rank]

    def get_sources(self, date = None):
        """
            Returns all the available sources given by the model
        """
        return self.report.get_sources(date)

    def get_dates(self):
        """
            Returns all the available dates given by the model
        """
        return self.report.get_dates()
    
    def get_as_infos(self, asn = None, source = None, date = None):
        """
            Get the data needed to display the page of the details on an AS 
        """
        as_infos, current_sources, raw_sources = [], [], []
        if asn is not None:
            graph_last_date = datetime.date.today()
            graph_first_date = datetime.date.today() - datetime.timedelta(days=self.days_graph)
            as_infos_temp, last_seen_sources, as_graph_infos = self.report.get_asn_descs(graph_first_date, graph_last_date, asn, source, date)
            if len(as_graph_infos) > 0 :
                self.make_graph(asn, as_graph_infos)
            if len(last_seen_sources) > 0:
                raw_sources = last_seen_sources.keys()
                current_sources = [ "{s}, last seen: {d}".format(s = source, d = date) for source, date in last_seen_sources.iteritems() ]
            if len(as_infos_temp) >= 0:
                as_infos = [ [a[0], a[1], a[2], a[3], a[4], ', '.join(a[5]), 1 + a[6]  ] for a in as_infos_temp]
        return as_infos, current_sources, raw_sources
    
    def get_ip_infos(self, asn = None, asn_tstamp = None, source = None, date = None):
        """
            Get the descriptions of the IPs of a subnet
        """
        if asn is not None and asn_tstamp is not None:
            ips_descs_temp = self.report.get_ips_descs(asn, asn_tstamp, source, date)
            return [ [ips_desc_temp[0], ', '.join(ips_desc_temp[1]) ] for ips_desc_temp in ips_descs_temp]
    
    def comparator(self, asns = None):
        """
            Get the data needed to display the page of the comparator
            FIXME: rewrite it!!
        """
        js_name = self.config.get('web','canvas_comparator_name')
        asns_to_return = []
        if asns is not None:
            splitted_asns = asns.split()
            g = GraphGenerator(js_name)
            title = ''
            for asn in splitted_asns:
                if asn.isdigit():
                    asns_to_return.append(asn)

                    graph_last_date = datetime.date.today()
                    graph_first_date = datetime.date.today() - datetime.timedelta(days=self.days_graph)
                    graph_dates = self.report.get_dates_from_interval(graph_first_date, graph_last_date)
                    dates_sources = self.report.get_all_sources(graph_dates)
                    all_ranks = self.report.get_all_ranks(asn, graph_dates, dates_sources)

                    data_graph, last_seen_sources = self.report.prepare_graphe_js(all_ranks, graph_dates, dates_sources)
                    g.add_line(data_graph, str(asn + self.report.ip_key), graph_first_date, graph_last_date)
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
        graph_last_date = datetime.date.today()
        graph_first_date = datetime.date.today() - datetime.timedelta(days=self.days_graph)
        g.add_line(infos, self.report.ip_key, graph_first_date, graph_last_date )
        g.set_title(asn)
        g.make_js()
        self.js = g.js
        self.js_name = js_name
