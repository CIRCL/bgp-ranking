#!/usr/bin/env python

import os
import cherrypy
from Cheetah.Template import Template


APPDIR = os.path.dirname(os.path.abspath(__file__))
INI_FILENAME = os.path.join(APPDIR, "config/cptest.ini")

import ConfigParser
import sys
config = ConfigParser.RawConfigParser()
config.read("../etc/bgp-ranking.conf")

server_root_dir =  config.get('global','root')
sys.path.append(os.path.join(server_root_dir,config.get('global','lib')))

from db_models.ranking import *


class Root(object):
    query_form = \
                """
                Please enter your query
                <form method="POST" action=".">
                  <input type="text" name="query" value="$query">
                  <input type="submit" value="Submit">
                </form> <br/>
                """

    def index(self, query = ""):
        if query == "":
            query = 'IP or AS Number'
            template = Template(self.query_form)
        else:
            entry = self.query_db(query)
            template = Template(self.query_form + "Your last query was $query.")
        template.query = query
        to_return = str(template)
        if entry is not None:
            to_return += '<br/>' + '<pre>' + entry + '</pre>'
        return to_return
    index.exposed = True
    
    def query_db(self, query):
        query_maker = WhoisQuery(int(config.get('whois_server','redis_db')))
        ip = None
        try:
            ip = IPy.IP(query)
        except:
            pass
        to_return = ''
        if ip:
            to_return = query_maker.whois_ip(ip)
        else:
           to_return = query_maker.whois_asn(query)
        
        return to_return


root = Root()


def main():
    cherrypy.quickstart(Root(), config = INI_FILENAME)


if __name__ == "__main__":
    main()
