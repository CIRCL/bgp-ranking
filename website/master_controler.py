import ConfigParser
import sys
import os
config = ConfigParser.RawConfigParser()
config.read("../etc/bgp-ranking.conf")
root_dir =  config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))
from ranking.reports import *

import datetime

class MasterControler():

    def __init__(self):
            pass

    def prepare_index(self, source = None, limit = 50, date = datetime.datetime.now()):
        self.report = Reports(date)
        self.report.best_of_day(limit, source)
        self.index_table = self.report.histories
    
    def get_sources(self):
        self.report.get_sources()
        self.sources = self.report.sources
    
    def get_as_infos(self, asn = None):
        self.report.get_asn_descs(int(asn))
        self.as_infos = self.report.asn_descs_to_print
        self.as_graph_infos = self.report.graph_infos
    
    def get_ip_infos(self, asn_desc = None):
        self.report.get_ips_descs(asn_desc)
        self.ip_infos = self.report.ip_descs_to_print
