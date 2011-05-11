#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Shadowserver Sinkhole
    ~~~~~~~~~~~~~~~~~~~~~

    Sinkhole list provided by Shadowserver
"""

from shadowserver import *
import dateutil.parser

class ShadowserverSinkhole(Shadowserver):
    """
        The subclass of Shadowserver which is used to parse the sinkhole
        reports of Shadowserver
    """
    directory = 'shadowserver/sinkhole/'
    
    def __init__(self, raw_dir):
        Shadowserver.__init__(self)
        self.directory = os.path.join(raw_dir, self.directory)

    def parse_line(self, line):
        """
        Parse a line 
        """
        ip = line[1]
        date = dateutil.parser.parse(line[0])
        infection = line[5]
        full_line =', '.join(line)
        return [ip, date, infection, full_line]
