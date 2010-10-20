#!/bin/python
# -*- coding: utf-8 -*-

"""
FIXME: not used anymore, generate a gnuplot graph
"""


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
gnuplot_static =  'set xlabel "Date"\n set ylabel "Rank"\n set xdata time \nset timefmt "%Y-%m-%d" \nset format x "%m/%d" \nset terminal png \n'

from sqlalchemy import desc

class ASGraf():
    
    def __init__(self, asn):
        self.asn = asn
    
    def save_graph(self):
        self.prepare_graf()
        self.make_graph()
    
    def prepare_graf(self):
        histories = History.query.filter_by(asn=int(self.asn)).order_by(desc(History.timestamp)).all()
        datav4 = os.path.join(graphs_dir, str(self.asn) + '_v4.dat' )
        datav6 = os.path.join(graphs_dir, str(self.asn) + '_v6.dat' )
        date = None
        tmptable = []
        for history in histories:
            prec_date = date
            date = history.timestamp.date()
            if date != prec_date:
                tmptable.append([str(history.timestamp.date()), str(history.rankv4), str(history.rankv6)] )
        v4 = open(datav4, 'w')
        v6 = open(datav6, 'w')
        for t in reversed(tmptable):
            v4.write(t[0] + '\t' + t[1] + '\n')
            v6.write(t[0] + '\t' + t[2] + '\n')
        v4.close()
        v6.close()
        self.filename_gnuplot = os.path.join(graphs_dir, str(self.asn) + '.gnu' )
        gnuplot = open(self.filename_gnuplot, 'w')
        gnuplot.write('set title "' + str(self.asn) + '"\n')
        gnuplot.write(gnuplot_static)
        gnuplot.write('set output "' + os.path.join(graphs_dir, str(self.asn) + '.png' ) + '"\n')
        gnuplot.write('plot "' + datav4 + '" using 1:2 title "IPv4" with linespoints \n')
        gnuplot.write('replot "' + datav6 + '" using 1:2 title "IPv6" with linespoints ')
        gnuplot.close()

    def make_graph(self):
        f = open("/dev/null","w")
        p = Popen(['gnuplot', self.filename_gnuplot], stdout=f, stderr=f)

class MetaGraph():
    
    def make_all_graphs(self):
        asns = ASNs.query.all()
        for asn in asns:
            a = ASGraf(asn.asn)
            a.save_graph()


if __name__ == "__main__":
    mg = MetaGraph()
    mg.make_all_graphs()
