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

from db_models.voting import *
import matplotlib
matplotlib.use('Agg')
from matplotlib.pyplot import figure, savefig
import matplotlib.pyplot as plt
from matplotlib.dates import DayLocator, HourLocator, DateFormatter
from numpy import arange

class ASGraf():
    
    def __init__(self, asn):
        self.asn = asn
    
    def save_graph(self, path):
        prepare_graf()
        make_graph(path)
    
    def prepare_graf(self):
        histories = History.query.filter_by(asn=int(self.asn)).all()
        if len(histories) == 0:
            return False
        rankingv4 = {}
        rankingv6 = {}
        for history in histories:
            rankingv4[history.timestamp.date()] = history.rankv4
            rankingv6[history.timestamp.date()] = history.rankv6
        self.datesv4 = [ d for d in rankingv4.keys() ]
        self.datesv6 = [ d for d in rankingv6.keys() ]
        self.rankv4 = [ t for t in rankingv4.values() ]
        self.rankv6 = [ t for t in rankingv6.values() ]
        return True
        
        
    def make_graph(self, save_path):
        fig = figure()
        ax = fig.add_subplot(111)
        ax.plot_date(self.datesv4, self.rankv4)
        ax.plot_date(self.datesv4, self.rankv4)

        ax.xaxis.set_major_locator( DayLocator() )
        ax.xaxis.set_minor_locator( HourLocator(arange(0,25,6)) )
        ax.xaxis.set_major_formatter( DateFormatter('%Y-%m-%d') )

        ax.fmt_xdata = DateFormatter('%Y-%m-%d %H:%M:%S')
        
        datemin = min(self.datesv4[0], self.datesv6[0]) - datetime.timedelta(days=1)
        datemax = max(self.datesv4[-1], self.datesv6[-1]) + datetime.timedelta(days=1)
        ax.set_xlim(datemin, datemax)

        maxrank = max(max(self.rankv4), max(self.rankv6)) + 0.5
        ax.set_ylim(0, maxrank)
        fig.autofmt_xdate()

        savefig(save_path)

class MetaGraph():
    graphs_dir = os.path.join(root_dir,config.get('directories','ranking_graphs'))
    
    def make_all_graphs(self):
        asns = ASNs.query.all()
        for asn in asns:
            a = ASGraf(asn)
            a.save_graph(graphs_dir + str(asn) + '.png')


if __name__ == "__main__":
    mg = MetaGraph()
    mg.make_all_graphs()
