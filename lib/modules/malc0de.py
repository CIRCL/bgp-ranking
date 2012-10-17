#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    malc0de parser
    ~~~~~~~~~~~~~~

    Class used to parse the daily files provided by DShield
"""

import re
import os
import datetime
import dateutil.parser
from modules.abstract_module import AbstractModule


class Malc0de(AbstractModule):

    def __init__(self, raw_dir):
        AbstractModule.__init__(self)
        self.directory = raw_dir

    def parse(self):
        self.ips = []
        for file in self.files:
            try:
                self.date = dateutil.parser.parse(re.findall('Last updated (.*)\n', open(file).read())[0])
            except:
                self.date = datetime.date.today()
            malc0de = open(file)
            for line in malc0de:
                ip = re.findall('((?:\d{1,3}\.){3}\d{1,3})[\s].*',line)
                if len(ip) == 0:
                    continue
                entry = self.prepare_entry(ip = ip[0], source = self.__class__.__name__, timestamp = self.date)
                self.put_entry(entry)
            malc0de.close()
            self.move_file(file)
