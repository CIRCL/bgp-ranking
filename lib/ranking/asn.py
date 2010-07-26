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
graphs_dir = os.path.join(root_dir,config.get('directories','ranking_graphs'))

from db_models.ranking import *
from db_models.voting import *
from subprocess import Popen
gnuplot_static =  "set xdata time \nset timefmt '%y-%m-%d' \nset format x '%y %m %d' \nset terminal png \n"

class ASGraf():
    
    def __init__(self, asn):
        self.asn = asn
    
    def save_graph(self, path):
        self.prepare_graf()
        self.make_graph(path)
    
    def prepare_graf(self):
        histories = History.query.filter_by(asn=int(self.asn)).all()
        datav4 = os.path.join(graphs_dir, str(self.asn) + '_v4.dat' )
        datav6 = os.path.join(graphs_dir, str(self.asn) + '_v6.dat' )
        v4 = open(datav4, 'w')
        v6 = open(datav6, 'w')
        for history in histories:
            v4 = write(history.timestamp.date() + '\t' + history.rankv4)
            v6 = write(history.timestamp.date() + '\t' + history.rankv6)
        v4.close()
        v6.close()
        self.filename_gnuplot = os.path.join(graphs_dir, str(self.asn) + '.gnu' )
        gnuplot = open(filename_gnuplot, 'w')
        gnuplot.write('set title "' + str(self.asn) + '"\n')
        gnuplot.write(gnuplot_static)
        gnuplot.write('set output "' + os.path.join(graphs_dir, str(self.asn) + 'png' ) + '"\n')
        gnuplot.write('plot "' + datav4 + '" using 1:2 with linespoints')
        gnuplot.write('replot "' + datav6 + '" using 1:2 with linespoints')
        gnuplot.close()

    def make_graph(self, save_path):
        p = Popen(['gnuplot', self.filename_gnuplot])

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
