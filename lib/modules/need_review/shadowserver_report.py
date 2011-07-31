#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Shadowserver Report 1
    ~~~~~~~~~~~~~~~~~~~~~

    First type of reports provided by Shadowserver
"""

from shadowserver import *
import dateutil.parser

class ShadowserverReport(Shadowserver):
    """
        The subclass of Shadowserver which is used to parse the
        first type of reports of Shadowserver
    """

    def __init__(self, raw_dir):
        self.directory = 'shadowserver/report/'
        Shadowserver.__init__(self)
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

