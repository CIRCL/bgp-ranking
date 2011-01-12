# -*- coding: utf-8 -*-

import os
import cherrypy
from cherrypy import _cperror
from Cheetah.Template import Template

import ConfigParser
import sys
import IPy
config = ConfigParser.RawConfigParser()
config.read("../etc/bgp-ranking.conf")
root_dir =  config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

config_file = config.get('web','config_file')
templates = config.get('web','templates')
website_root = config.get('web','website_root')
css_file = config.get('web','css_file')
website_images_dir = config.get('web','images')

rgraph_dir = 'RGraph/'
rgraph_scripts = ['RGraph.common.core.js', 'RGraph.common.zoom.js', 'RGraph.common.resizing.js', 'RGraph.common.context.js', 'RGraph.line.js', 'RGraph.common.tooltips.js']

from master_controler import MasterControler

graphes_dir = os.path.join(root_dir,config.get('web','graphes'))

class Master(object):
    
    def __init__(self):
        self.controler = MasterControler()
    
    def init_template(self, source = None):
        source = self.reset_if_empty(source)
        self.template.rgraph_dir = rgraph_dir
        self.template.rgraph_scripts = rgraph_scripts
        self.template.css_file = css_file
        self.controler.get_sources()
        self.template.sources = self.controler.sources
        self.template.source = source
    
    def reset_if_empty(self, to_check = None):
        if to_check is not None and len(to_check) == 0:
            return None
        return to_check
    
    def asns(self, source = None, asn = None):
        source = self.reset_if_empty(source)
        asn = self.reset_if_empty(asn)
        if asn is not None:
            return self.asn_details(source, asn)
        self.template = Template(file = os.path.join(website_root, templates, 'index_asn.tmpl'))
        self.init_template(source)
        self.controler.prepare_index(source)
        self.template.histories = self.controler.histories
        return str(self.template)
    asns.exposed = True
    
    def asn_details(self, source = None, asn = None, ip_details = None):
        asn = self.reset_if_empty(asn)
        source = self.reset_if_empty(source)
        ip_details = self.reset_if_empty(ip_details)
        self.template = Template(file = os.path.join(website_root, templates, 'asn_details.tmpl'))
        self.init_template(source)
        self.controler.js = self.controler.js_name = None
        if asn is not None:
            asn = asn.lstrip('AS')
            if asn.isdigit():
                self.template.asn = asn
                as_infos = self.controler.get_as_infos(asn, source)
                if as_infos is not None: 
                    self.template.asn_descs = as_infos
                    #if len(self.template.asn_descs) is not None:
                    self.template.javascript = self.controler.js
                    self.template.js_name = self.controler.js_name
                    if ip_details is not None:
                        self.template.ip_details = ip_details
                        self.template.ip_descs = self.controler.get_ip_infos(asn, ip_details, source)
                    else:
                        self.template.error = "No data for " + asn + " on " + source
                else:
                    self.template.error = asn + " not found in the database."
            else: 
                self.template.error = "Invalid query: " +  asn
            if self.template.javascript is None:
                self.template.error = "No data available to generate the graph for "+ asn
            return str(self.template)
        else:
            return str(self.default())
    asn_details.exposed = True
    
    def comparator(self, source = None, asns = None):
        asns = self.reset_if_empty(asns)
        source = self.reset_if_empty(source)
        self.template = Template(file = os.path.join(website_root, templates, 'comparator.tmpl'))
        self.init_template(source)
        self.template.asns = asns
        if self.template.asns is not None:
            self.controler.comparator(self.template.asns)
            self.template.js_comparator = self.controler.js
            self.template.js_comparator_name = self.controler.js_name
            if self.template.js_comparator is None:
                self.template.error = "No valid ASN in the list..."
        return str(self.template)
    comparator.exposed = True

    def reload(self):
        self.controler = MasterControler()
        return self.default()
    reload.exposed = True

    def default(self):
        return str(self.asns())
    default.exposed = True

def error_page_404(status, message, traceback, version):
    return "Error %s - This page does not exist." % status

if __name__ == "__main__":
    website = Master()
    
    def handle_error():
        website = Master()
        cherrypy.response.status = 500
        cherrypy.response.body = ["<html><body>Sorry, an error occured</body></html>"]
    
    _cp_config = {'request.error_response': handle_error}
    
    cherrypy.config.update({'error_page.404': error_page_404})
    cherrypy.quickstart(website, config = config_file)
