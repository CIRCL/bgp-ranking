# -*- coding: utf-8 -*-

from shadowserver import *
import dateutil.parser

class ShadowserverReport2(Shadowserver):
    name = 'Shadowserver report 2'
    directory = 'datas/shadowserver/report2/'
    
    def parse_line(self, line):
        ip = line[1]
        date = dateutil.parser.parse(line[0])
        infection = line[9]
        full_line =', '.join(line)
        return [ip, date, infection, full_line]
