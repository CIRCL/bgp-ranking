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
from db_models.ranking import *
from db_models.voting import *


config_file = config.get('web','config_file')
templates = config.get('web','templates')
website_root = config.get('web','website_root')
css_file = config.get('web','css_file')
website_images_dir = config.get('web','images')

graphes_dir = os.path.join(root_dir,config.get('web','graphes'))

class Master(object):
    
    def __init__(self):
        self.report = Reports()
        self.report.best_of_day()
    
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

