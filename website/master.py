# -*- coding: utf-8 -*-
"""
    View class of the website
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    The website respects the MVC pattern and this class is the view.

"""

import os
import cherrypy
from cherrypy import _cperror
from Cheetah.Template import Template
import ConfigParser
import sys
import IPy
from master_controler import MasterControler
import cgi

class Master(object):
    
    def __init__(self):
        self.config = ConfigParser.RawConfigParser()
        config_file = "/path/to/bgp-ranking.conf"
        self.config.read(config_file)

        self.templates = config.get('web','templates')
        self.website_root = os.path.join(self.config.get('directories','root'),\
                                            config.get('web','root_web'))
        
        self.rgraph_scripts = [ 'RGraph.common.core.js',\
                                'RGraph.common.zoom.js', \
                                'RGraph.common.resizing.js',\
                                'RGraph.common.context.js',\
                                'RGraph.line.js',\
                                'RGraph.common.tooltips.js']
        self.controler = MasterControler()
        
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def json(self, source = None, date = None, asn = None, ip_details = None):
        source = self.reset_if_empty(source)
        date = self.reset_if_empty(date)
        asn = self.reset_if_empty(asn)
        ip_details = self.reset_if_empty(ip_details)

        to_return = {}
        to_return["dates"] = list(sorted(self.controler.get_dates()))
        if asn is not None:
            temp_as_info = self.controler.get_as_infos(asn, source, date)
            to_return["sources"] = list(temp_as_info[1])
            to_return["asn"] = list(temp_as_info[0])
            if ip_details is not None and len(temp_as_info[0]) > 0:
                to_return["ip"] = list(self.controler.get_ip_infos(asn, ip_details, source, date))
        else:
            to_return["sources"] = list(self.controler.get_sources(date))
            to_return["ranking"] = list(self.controler.prepare_index(source, date))
        return to_return

    def init_template(self, source = None, date = None):
        """
            Initialize the basic components of the template
        """
        source = self.reset_if_empty(source)
        date = self.reset_if_empty(date)
        self.template.rgraph_dir = config.get('web','rgraph_dir')
        self.template.rgraph_scripts = self.rgraph_scripts
        self.template.css_file = self.config.get('web','css_file')
        self.template.logo     = self.config.get('web','logo')
        self.template.banner   = self.config.get('web','banner')
        self.template.sources = self.controler.get_sources(date)
        self.template.dates = sorted(self.controler.get_dates())
        self.template.source = source
        self.template.date = date
    
    def escape(self, var):
        return cgi.escape(var)

    def reset_if_empty(self, to_check = None):
        """
            Ensure the empty paramaters are None before doing anything
        """
        if to_check is None or len(to_check) == 0:
            return None
        return self.escape(to_check)

    @cherrypy.expose
    def asns(self, source = None, asn = None, date = None):
        """
            Generate the view of the global ranking
        """
        source = self.reset_if_empty(source)
        asn = self.reset_if_empty(asn)
        date = self.reset_if_empty(date)
        if asn is not None:
            return self.asn_details(source = source, asn = asn, date = date)
        histo = self.controler.prepare_index(source, date)
        self.template = Template(file = os.path.join(self.website_root, self.templates, 'index_asn.tmpl'))
        self.init_template(source, date)
        self.template.histories = histo
        return str(self.template)

    @cherrypy.expose
    def asn_details(self, source = None, asn = None, ip_details = None, date = None):
        """
            Generate the view of an ASN 
        """
        asn = self.reset_if_empty(asn)
        source = self.reset_if_empty(source)
        ip_details = self.reset_if_empty(ip_details)
        date = self.reset_if_empty(date)
        self.template = Template(file = os.path.join(self.website_root, self.templates, 'asn_details.tmpl'))
        self.init_template(source, date)
        self.controler.js = self.controler.js_name = None
        if asn is not None:
            asn = asn.lstrip('AS')
            if asn.isdigit():
                self.template.asn = asn
                as_infos, current_sources = self.controler.get_as_infos(asn, source, date)
                if as_infos is not None:
                    self.template.sources = self.controler.get_sources(date)
                    self.template.dates = sorted(self.controler.get_dates())
                    self.template.asn_descs = as_infos
                    self.template.current_sources = current_sources
                    self.template.javascript = self.controler.js
                    self.template.js_name = self.controler.js_name
                    if ip_details is not None:
                        self.template.ip_details = ip_details
                        self.template.ip_descs = self.controler.get_ip_infos(asn, ip_details, source, date)
                else:
                    self.template.error = asn + " not found in the database."
            else: 
                self.template.error = "Invalid query: " +  asn
            if self.template.javascript is None:
                self.template.error = "No data available to generate the graph for "+ asn
            return str(self.template)
        else:
            return str(self.default())

    @cherrypy.expose
    def comparator(self, source = None, asns = None):
        """
            Generate the view comparing a set of ASNs
        """
        asns = self.reset_if_empty(asns)
        source = self.reset_if_empty(source)
        self.template = Template(file = os.path.join(self.website_root, self.templates, 'comparator.tmpl'))
        self.init_template(source)
        if asns is not None:
            self.template.asns = self.controler.comparator(asns)
            self.template.sources = self.controler.get_sources()
            self.template.js_comparator = self.controler.js
            self.template.js_comparator_name = self.controler.js_name
            if self.template.js_comparator is None:
                self.template.error = "No valid ASN in the list..."
        return str(self.template)

    @cherrypy.expose
    def reload(self):
        """
            Recompute all the ranks and return on the index
        """
        self.controler = MasterControler()
        return self.default()

    @cherrypy.expose
    def default(self):
        """
            Load the index
        """
        return str(self.asns())

def error_page_404(status, message, traceback, version):
    """
        Display an error if the page does not exists
    """
    return "Error %s - This page does not exist." % status

if __name__ == "__main__":
    config = ConfigParser.RawConfigParser()
    config_file = "/path/to/bgp-ranking.conf"
    config.read(config_file)
    
    website = Master()
    
    def handle_error():
        website = Master()
        cherrypy.response.status = 500
        cherrypy.response.body = ["<html><body>Sorry, an error occured</body></html>"]
    
    _cp_config = {'request.error_response': handle_error}
    
    cherrypy.config.update({'error_page.404': error_page_404})
    cherrypy.quickstart(website, config = config.get('web','config_file'))
