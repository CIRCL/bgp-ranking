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
rgraph_scripts = ['RGraph.common.core.js', 'RGraph.line.js']

from master_controler import MasterControler

graphes_dir = os.path.join(root_dir,config.get('web','graphes'))

class Master(object):
    
    def __init__(self):
        self.controler = MasterControler()
        self.init_template()
        self.init_index()
    
    def init_template(self):
        self.template = Template(file = os.path.join(website_root, templates, 'master.tmpl'))
        self.template.rgraph_dir = rgraph_dir
        self.template.rgraph_scripts = rgraph_scripts
        self.template.title = 'index'
        self.template.css_file = css_file
    
    def init_index(self, source = None):
        self.controler.prepare_index(source = source)
        self.template.histories = self.controler.index_table
        self.controler.get_sources()
        self.template.sources = self.controler.sources
        self.template.asn_descs = None 
        self.template.ip_descs = None
        self.template.query = None
        self.template.source = source
    
    def set_graph_infos(self):
        infos = self.controler.as_graph_infos
        self.template.ipv4_js = infos[0]
        self.template.ipv6_js = infos[1]
        self.template.dates_js = infos[2]
        self.template.max_js = infos[3]
    
    def reload(self, source = None):
        self.init_index()
        return str(self.template)
    reload.exposed = True

    def default(self, query = None, ip_details = None, source = None):
        if query is None or len(query) == 0:
            self.init_index(source)
        else:
            query = query.lstrip('AS')
            if query.isdigit():
                self.template.query = query
                self.controler.get_as_infos(query)
                self.template.asn_descs = self.controler.as_infos
                self.set_graph_infos()
                if ip_details is not None:
                    self.template.ip_details = ip_details
                    self.controler.get_ip_infos(ip_details)
                    self.template.ip_descs = self.controler.ip_infos
            else: 
                self.template.error = "Invalid query: " +  query
                self.init_index(source)
        return str(self.template)
    default.exposed = True

if __name__ == "__main__":
    cherrypy.quickstart(Master(), config = config_file)

