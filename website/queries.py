#!/usr/bin/env python

import os
import cherrypy
from Cheetah.Template import Template


APPDIR = os.path.dirname(os.path.abspath(__file__))
INI_FILENAME = os.path.join(APPDIR, "config/bgp-ranking_website.ini")

import ConfigParser
import sys
config = ConfigParser.RawConfigParser()
config.read("../etc/bgp-ranking.conf")

server_root_dir =  config.get('global','root')
sys.path.append(os.path.join(server_root_dir,config.get('global','lib')))
website_root_dir =  os.path.join(server_root_dir,config.get('website','root'))
website_images_dir =  os.path.join(website_root_dir,config.get('website','images'))

from db_models.ranking import *

from graph.ip import *
from graph.asn import *

import IPy

class Queries(object):

    def index(self, query = ""):
        filename = os.path.join(APPDIR, "querying.tmpl")
        self.template = Template(file = filename)
        entry = None
        if query != "":
            self.query_db(query)
        return str(self.template)
    index.exposed = True
    
    def query_db(self, query):
        ip = None
        try:
            ip = IPy.IP(query)
        except:
            pass
        if ip is not None:
            descriptions = IPsDescriptions.query.filter_by(ip=IPs.query.filter_by(ip=unicode(ip)).first()).all()
            self.template.last_query = query
            if len(descriptions) > 0:
                self.template.query = query
                self.template.whois_entry = ''
                print descriptions
                for description in descriptions:
                    self.template.whois_entry += str(description.whois) + '\n'
                if self.make_ip_graf(query, descriptions):
                    self.template.image = query
        else:
            query = query[2:]
            descriptions = ASNsDescriptions.query.filter_by(asn=ASNs.query.filter_by(asn=unicode(query)).first()).all()
            self.template.last_query = 'AS' + query
            if len(descriptions) > 0:
                self.template.query = self.template.last_query
                self.template.whois_entry = ''
                for description in descriptions:
                    self.template.whois_entry = description.owner
                if self.make_asn_graf(query, descriptions):
                    self.template.image = query
            

    
    def make_ip_graf(self, query, descriptions):
        graf = IPGraf(query)
        if graf.prepare_graf(descriptions):
            graf.make_graph(os.path.join(website_images_dir,query) + '.png')
            return True
        else:
            return False
            
    def make_asn_graf(self, query, descriptions):
        graf = ASGraf(query)
        if graf.prepare_graf(descriptions):
            graf.make_graph(os.path.join(website_images_dir,query) + '.png')
            return True
        else:
            return False

def main():
    cherrypy.quickstart(Queries(), config = INI_FILENAME)


if __name__ == "__main__":
    main()
