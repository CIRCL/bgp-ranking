#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    CleanMX parser
    ~~~~~~~~~~~~~~

    The default parser of CleanMX lists
"""

import datetime
import re

from modules.abstract_module import AbstractModule

class CleanMXDefault(AbstractModule):
    """
        Parser
    """

    def __init__(self, raw_dir):
        AbstractModule.__init__(self)
        self.directory = raw_dir


    def parse(self):
        """
            Parse the list
        """
        self.date = datetime.date.today()
        self.ips = []
        for file in self.files:
            f = open(file)
            for line in f:
                # FIXME ensure it is correct
                ip = re.findall('<(?:ip|review)>((?:\d{1,3}\.){3}\d{1,3})<.*',line)
                if len(ip) == 0:
                    continue
                entry = self.prepare_entry(ip = ip[0], source = self.__class__.__name__, timestamp = self.date)
                self.put_entry(entry)
            self.move_file(file)
