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

rgraph_dir = os.path.join(root_dir,config.get('directories','rgraph'))
rgraph_to_import = ['RGraph.common.js', 'RGraph.line.js']
html_scripts = ""
for js in rgraph_to_import:
    html_scripts += '<script src="'+ js +'">\n'
#canvas = '<canvas id="ASN_graph" width="300" height="100">[No canvas support]</canvas>'



graphes_dir = os.path.join(root_dir,config.get('web','graphes'))

class Master(object):
    
    def __init__(self):
        self.report = Reports()
        self.report.best_of_day()
        self.template.include_scripts = html_scripts
    
    def reload(self):
        self.report.best_of_day()
        self.template.asn_descs = None 
        self.template.ip_descs = None
        return self.default()
    reload.exposed = True

    def default(self, query = "", ip_details = ""):
        filename = os.path.join(website_root, templates, 'master.tmpl')
        self.template = Template(file = filename)
        self.template.title = 'index'
        self.template.css_file = css_file
        self.template.query = query
        if query == "":
            self.template.histories = self.report.histories
        else:
            self.template.query = query.lstrip('AS')
            if self.template.query.isdigit():
                self.template.graph = 'images/' + self.template.query + '.png'
                
                self.report.prepare_graphes_js(self.template.query)
                self.template.js_graph_script = self.report.script
                
                self.report.get_asn_descs(self.template.query)
                self.template.asn_descs = self.report.asn_descs
                self.template.ip_details = ip_details
                if ip_details != "":
                    self.report.get_ips_descs(ip_details)
                    self.template.ip_descs = self.report.ip_descs
            else: 
               self.template.infomessage = 'The query can be AS<number> or <number>.' 
        return str(self.template)
    default.exposed = True

if __name__ == "__main__":
    cherrypy.quickstart(Master(), config = config_file)

