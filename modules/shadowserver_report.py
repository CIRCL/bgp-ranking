# -*- coding: utf-8 -*-

from shadowserver import *
import dateutil.parser

class ShadowserverReport(Shadowserver):
    name = 'Shadowserver report'
    directory = 'datas/shadowserver/report/'
    
    def parse_line(self, line):
        ip = line[1]
        date = dateutil.parser.parse(line[0])
        infection = line[11]
        full_line =', '.join(line)
        return [ip, date, infection, full_line]
        
