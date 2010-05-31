#!/bin/python
# -*- coding: utf-8 -*-


class IPGraf():
    
    from pylab import figure, show
    from matplotlib.dates import DateFormatter
    import datetime

    
    def __init__(self, ip):
        self.ip = ip
    
    def prepare_graf(self):
        descriptions = IPsDescriptions.query.filter_by(ip=IPs.query.filter_by(ip=unicode('72.47.209.133')).first()).all()
        datas_tmp = []
        for desc in descriptions:
            datas_tmp.append( [ desc.timestamp.date(), desc.times ] )

        datas = {}
        for tmp in datas_tmp:
           data = datas.get(tmp[0], None)
           if data is None:
               datas[tmp[0]] = tmp[1]
           else:
               datas[tmp[0]] += tmp[1]

        self.dates = [ d for d in datas.keys() ]
        self.times = [ t for t in datas.values() ]

    def make_graph(self):
        fig = figure()
        ax = fig.add_subplot(111)
        ax.plot_date(self.dates, self.times, '-')

        ax.autoscale_view()

        # format the coords message box
        def price(x): return '$%1.2f'%x
        ax.fmt_xdata = DateFormatter('%Y-%m-%d')
        ax.fmt_ydata = price
        ax.grid(True)

        fig.autofmt_xdate()
        pylab.savefig('Fig1.png')
#        show()




if __name__ == "__main__":
    import ConfigParser
    import sys
    import os
    config = ConfigParser.RawConfigParser()
    config.read("../../etc/bgp-ranking.conf")

    server_root_dir =  config.get('global','root')
    sys.path.append(os.path.join(server_root_dir,config.get('global','lib')))
    from db_models.ranking import *
    
    def usage():
        print "ip.py ip"
        exit(1)

    if len(sys.argv) < 2:
        usage()

    query = sys.argv[1]
