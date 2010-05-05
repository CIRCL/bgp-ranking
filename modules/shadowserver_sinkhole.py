# -*- coding: utf-8 -*-

from shadowserver import *
import dateutil.parser

class ShadowserverSinkhole(Shadowserver):
    name = 'Shadowserver sinkhole'
    directory = 'datas/shadowserver/sinkhole/'
    
    def parse_line(self, line):
        """
        Parse a line 
        """
        ip = line[1]
        date = dateutil.parser.parse(line[0])
        infection = line[5]
        full_line =', '.join(line)
        return [ip, date, infection, full_line]
