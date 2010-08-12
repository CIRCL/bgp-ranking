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
from ranking.reports import *

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
        self.init_index()
    
    def init_template(self):
        self.template.rgraph_dir = rgraph_dir
        self.template.rgraph_scripts = rgraph_scripts
        self.template.css_file = css_file
    
    def init_index(self, source = None):
        self.template = Template(file = os.path.join(website_root, templates, 'index.tmpl'))
        self.init_template()
        
        self.controler.prepare_index(source = source)
        self.controler.get_sources()
        
        self.template.histories = self.controler.index_table
        self.template.sources = self.controler.sources
        self.template.source = source
    
    def init_asn_details(self, query = None, ip_details = None):
        self.template = Template(file = os.path.join(website_root, templates, 'asn_details.tmpl'))
        self.init_template()
        query = query.lstrip('AS')
        if query.isdigit():
            self.template.query = query
            self.controler.get_as_infos(query)
            self.template.asn_descs = self.controler.as_infos
            self.template.javascript = self.controler.js
            self.template.js_name = self.controler.js_name
            if ip_details is not None:
                self.template.ip_details = ip_details
                self.controler.get_ip_infos(ip_details)
                self.template.ip_descs = self.controler.ip_infos
        else: 
            self.template.error = "Invalid query: " +  query
            self.init_index(source)
    
    def comparator(self, asns = None):
        self.controler.comparator(asns)
        self.template.js_comparator = self.controler.js
        self.template.js_comparator_name = self.controler.js_name
        return str(self.template)
    comparator.exposed = True
        
    
    def reload(self, source = None):
        self.init_index()
        return str(self.template)
    reload.exposed = True

    def default(self, query = None, source = None):
        if query is None or len(query) == 0:
            self.init_index(source)
        else:
            self.init_asn_details(query)
        return str(self.template)
    default.exposed = True

if __name__ == "__main__":
    cherrypy.quickstart(Master(), config = config_file)

