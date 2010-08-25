# -*- coding: utf-8 -*-

import os
import cherrypy
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
        self.template.rgraph_dir = rgraph_dir
        self.template.rgraph_scripts = rgraph_scripts
        self.template.css_file = css_file
        self.controler.get_sources()
        self.template.sources = self.controler.sources
        self.template.source = source
    
    def asns(self, source = None, asn = None):
        self.template = Template(file = os.path.join(website_root, templates, 'index_asn.tmpl'))
        self.init_template(source)
        self.controler.prepare_index(source)
        self.template.histories = self.controler.histories
        return str(self.template)
    asns.exposed = True
    
    def asn_details(self, source = None, asn = None, ip_details = None):
        self.template = Template(file = os.path.join(website_root, templates, 'asn_details.tmpl'))
        self.init_template(source)
        if asn is not None and len(asn) > 0:
            asn = asn.lstrip('AS')
            if asn.isdigit():
                self.template.asn = asn
                self.controler.get_as_infos(asn, source)
                if self.controler.as_infos is not None: 
                    self.template.asn_descs = self.controler.as_infos
                    if len(self.template.asn_descs) > 0:
                        self.template.javascript = self.controler.js
                        self.template.js_name = self.controler.js_name
                        if ip_details is not None and ip_details.isdigit():
                            self.template.ip_details = ip_details
                            self.controler.get_ip_infos(ip_details, source)
                            self.template.ip_descs = self.controler.ip_infos
                            return str(self.template)
                    else:
                        self.template.error = "No data for " + asn + " on " + source
                else:
                    self.template.error = asn + " not found in the database."
            else: 
                self.template.error = "Invalid query: " +  asn
        return str(self.default())
    asn_details.exposed = True
    
    def comparator(self, source = None, asns = None):
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
        return self.default()
    reload.exposed = True

    def default(self):
        return str(self.asns())
    default.exposed = True

if __name__ == "__main__":
    cherrypy.quickstart(Master(), config = config_file)

