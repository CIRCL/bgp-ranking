#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Map
    ~~~
    
    Generate the data used to display the world map
"""

from socket import *
import json
import os
import redis


if __name__ == '__main__':
    import ConfigParser
    import sys
    config = ConfigParser.RawConfigParser()
    config_file = "/home/rvinot/bgp-ranking/etc/bgp-ranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sleep_timer = int(config.get('ranking','bview_check'))
    sleep_timer_short = int(config.get('sleep_timers','short'))
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

from helpers.common_report import CommonReport

class Map(CommonReport):

    def __init__(self):
        CommonReport.__init__(self, 4)
        date = self.get_default_date()[1]
        self.histo_key = date + "|global|rankv4"
        ranks = self.history_db_temp.zrevrange(self.histo_key, 0, -1)
        self.asns = ["begin", "verbose"]
        [self.asns.append("AS" + asn) for asn in ranks]
        self.asns.append("end")


    def get_country_codes(self):
        s = socket(AF_INET, SOCK_STREAM)
        self.responses = []
        s.connect(("whois.cymru.com", 43))
        s.send(self.asns[0] + "\n")
        s.recv(1024)
        s.send(self.asns[1] + "\n")
        for asn in self.asns[2:-2]:
            s.send(asn + "\n")
        s.send(self.asns[-1] + "\n")
        fs = s.makefile()
        for asn in self.asns[2:-2]:
            self.responses.append(fs.readline(1024))
        s.close()

    def generate(self):
        values = {}
        for response in self.responses:
            splitted = response.split("|")
            if len(splitted[1].strip()) == 0:
                continue
            if values.get(splitted[1].strip()) is None:
                values[splitted[1].strip()] = self.history_db_temp.zscore(self.histo_key, splitted[0].strip())
            else:
                values[splitted[1].strip()] += self.history_db_temp.zscore(self.histo_key, splitted[0].strip())
        js_file = os.path.join( self.config.get('directories','root'),\
                                self.config.get('web','root_web'),\
                                self.config.get('web','map_data'))
        f = open(js_file, "w")
        f.write("var stats =\n" + json.dumps(values))
        f.close()

if __name__ == '__main__':
    m = Map()
    m.get_country_codes()
    m.generate()
