#!/bin/python
# -*- coding: utf-8 -*-

import datetime
from matplotlib.pyplot import figure, savefig
from matplotlib.dates import DayLocator, HourLocator, DateFormatter
from numpy import arange

class AbstractGraf():
    
    def __init__(self, ip):
        self.ip = ip


    def make_graph(self, save_path):
        fig = figure()
        ax = fig.add_subplot(111)
        ax.plot_date(self.dates, self.times)

        ax.xaxis.set_major_locator( DayLocator() )
        ax.xaxis.set_minor_locator( HourLocator(arange(0,25,6)) )
        ax.xaxis.set_major_formatter( DateFormatter('%Y-%m-%d') )

        ax.fmt_xdata = DateFormatter('%Y-%m-%d %H:%M:%S')
        
        datemin = self.dates[0] - datetime.timedelta(days=1)
        datemax = self.dates[-1] + datetime.timedelta(days=1)
        ax.set_xlim(datemin, datemax)

        maxtimes = max(self.times) +1
        ax.set_ylim(0, maxtimes)


        
        fig.autofmt_xdate()

        savefig(save_path)
