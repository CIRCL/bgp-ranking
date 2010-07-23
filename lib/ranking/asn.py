#!/bin/python
# -*- coding: utf-8 -*-


import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.optionxform = str
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('directories','root')
sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

from db_models.ranking import *
from db_models.voting import *
import Gnuplot, Gnuplot.funcutils


class ASGraf():
    
    def __init__(self, asn):
        self.asn = asn
    
    def save_graph(self, path):
        self.prepare_graf()
        self.make_graph(path)
    
    def prepare_graf(self):
        histories = History.query.filter_by(asn=int(self.asn)).all()
        if len(histories) == 0:
            return False
        rankingv4 = []
        rankingv6 = []
        for history in histories:
            rankingv4.append([history.timestamp.date(), history.rankv4])
            rankingv6.append([history.timestamp.date(), history.rankv6])
        return True
        
        
    def make_graph(self, save_path):
		g = Gnuplot.Gnuplot(persist=1)
		g.title('Ranking ASN: ' + self.asn)
#		g('set data style line')
		g.replot(self.rankingv4)
		g.plot(self.rankingv6)
		g.save(save_path)

class MetaGraph():
    graphs_dir = os.path.join(root_dir,config.get('directories','ranking_graphs'))
    
    def make_all_graphs(self):
        asns = ASNs.query.all()
        for asn in asns:
            a = ASGraf(asn.asn)
            a.save_graph(self.graphs_dir + str(asn.asn) + '.png')


if __name__ == "__main__":
    mg = MetaGraph()
    mg.make_all_graphs()
