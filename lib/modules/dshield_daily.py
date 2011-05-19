#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    DShield daily parser
    ~~~~~~~~~~~~~~~~~~~~

    Class used to parse the daily files provided by DShield
"""

import re
import os
import dateutil.parser
from modules.abstract_module import AbstractModule


class DshieldDaily(AbstractModule):

    def __init__(self, raw_dir):
        AbstractModule.__init__(self)
        self.directory = raw_dir

    def parse(self):
        """ 
            Parse the list
        """
        self.ips = []
        for file in self.files:
            self.date = dateutil.parser.parse(re.findall('updated (.*)\n', open(file).read())[0])
            daily = open(file)
            for line in daily:
                ip = re.findall('((?:\d{1,3}\.){3}\d{1,3})[\s].*',line)
                if len(ip) == 0:
                    continue
                entry = self.prepare_entry(ip = ip[0], source = self.__class__.__name__, timestamp = self.date)
                self.put_entry(entry)
            daily.close()
            self.move_file(file)
