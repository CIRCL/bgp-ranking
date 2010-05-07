# -*- coding: utf-8 -*-

from shadowserver import *
import dateutil.parser

class ShadowserverReport(Shadowserver):
    name = 'Shadowserver report'
    directory = 'shadowserver/report/'
    
    def __init__(self, raw_dir):
        IPUpdate.__init__(self)
        self.directory = os.path.join(raw_dir, self.directory)
    
    def parse_line(self, line):
        """
        Parse a line 
        """
        ip = line[1]
        date = dateutil.parser.parse(line[0])
        infection = line[11]
        full_line =', '.join(line)
        return [ip, date, infection, full_line]
        
