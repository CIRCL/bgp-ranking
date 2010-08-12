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
        self.index()
    
    def init_template(self):
        self.template.rgraph_dir = rgraph_dir
        self.template.rgraph_scripts = rgraph_scripts
        self.template.css_file = css_file
        self.controler.get_sources()
        self.template.sources = self.controler.sources
    
    def index(self, source = None):
        self.template = Template(file = os.path.join(website_root, templates, 'index.tmpl'))
        self.init_template()
        self.controler.prepare_index(source)
        self.template.histories = self.controler.index_table
    
    def asn_details(self, asn = None, ip_details = None):
        self.template = Template(file = os.path.join(website_root, templates, 'asn_details.tmpl'))
        self.init_template()
        if asn is not None and len(asn) > 0:
            asn = asn.lstrip('AS')
            if asn.isdigit():
                self.template.asn = asn
                self.controler.get_as_infos(asn)
                self.template.asn_descs = self.controler.as_infos
                if self.template.asn_descs is not None:
                    self.template.javascript = self.controler.js
                    self.template.js_name = self.controler.js_name
                    if ip_details is not None:
                        self.template.ip_details = ip_details
                        self.controler.get_ip_infos(ip_details)
                        self.template.ip_descs = self.controler.ip_infos
                else:
                    self.template.error = asn + " not Found"
            else: 
                self.template.error = "Invalid query: " +  asn
                self.index()
        else:
            self.index()
        return str(self.template)
    asn_details.exposed = True
    
    def comparator(self, asns = None):
        self.controler.comparator(asns)
        self.template.js_comparator = self.controler.js
        self.template.js_comparator_name = self.controler.js_name
        return str(self.template)
    comparator.exposed = True
        
    
    def reload(self):
        self.index()
        return str(self.template)
    reload.exposed = True

    def default(self, source = None):
        self.index(source)
        return str(self.template)
    default.exposed = True

if __name__ == "__main__":
    cherrypy.quickstart(Master(), config = config_file)

