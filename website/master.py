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

    def default(self, query = ""):
        filename = os.path.join(website_root, templates, 'master.tmpl')
        self.template = Template(file = filename)
        self.template.title = 'index'
        self.template.css_file = css_file
        self.template.query = query
        if query == "":
            self.template.histories = self.report.histories
        else:
            self.template.graph = 'images/' + query + '.png'
            self.report.get_asn_descs(self.template.query)
            self.template.asn_descs = self.report.asn_descs
            if ip_details != "":
                self.report.get_ips_descs(ip_details)
                self.template.ip_descs = self.report.ip_descs
        return str(self.template)
    default.exposed = True

#    def query_db(self, query):
#        ip = None
#        try:
#            ip = IPy.IP(query)
#        except:
#            pass
#        self.template.whois_entry = ''
#        if ip is not None:
#            descriptions = IPsDescriptions.query.filter_by(ip=IPs.query.filter_by(ip=unicode(ip)).first()).all()
#            self.template.query = query
#            if len(descriptions) > 0:
#                for description in descriptions:
#                    self.template.whois_entry += str(description.whois) + '\n'
#                if self.make_ip_graf(query, descriptions):
#                    self.template.image = query
#        else:
#            query = query[2:]
#            report = Reports()
#            report.best_of_day()
#            descriptions = ASNsDescriptions.query.filter_by(asn=ASNs.query.filter_by(asn=unicode(query)).first()).all()
#            self.template.query = 'AS' + query
#            if len(descriptions) > 0:
#                for description in descriptions:
#                    self.template.whois_entry = description.owner
#                if self.make_asn_graf(query, descriptions):
#                    self.template.image = query
#        if self.template.whois_entry == '':
#            self.template.whois_entry = 'Nothing found in the database'
#
#    def make_ip_graf(self, query, descriptions):
#        graf = IPGraf(query)
#        if graf.prepare_graf(descriptions):
#            graf.make_graph(os.path.join(website_images_dir,query) + '.png')
#            return True
#        else:
#            return False
#
#    def make_asn_graf(self, query, descriptions):
#        graf = ASGraf(query)
#        if graf.prepare_graf(descriptions):
#            graf.make_graph(os.path.join(website_images_dir,query) + '.png')
#            return True
#        else:
#            return False

if __name__ == "__main__":
    cherrypy.quickstart(Master(), config = config_file)

