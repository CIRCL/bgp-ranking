#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    autoshun parser
    ~~~~~~~~~~~~~~

    Class used to parse the files provided by Autoshun
"""

import datetime
#import dateutil.parser
import csv
from modules.abstract_module import AbstractModule


class Shunlist(AbstractModule):

    def __init__(self, raw_dir):
        AbstractModule.__init__(self)
        self.directory = raw_dir

    def parse(self):
        self.date = datetime.date.today()
        self.ips = []
        for file in self.files:
            with open(file, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=',')
                for line in reader:
                    if len(line) < 3:
                        continue
                    ip = line[0]
                    # The timestamp change many times each day.
                    # It breaks the ranking
                    # date = dateutil.parser.parse(line[1])
                    #comment = line[2]
                    entry = self.prepare_entry(ip = ip,
                            source = self.__class__.__name__,
                            timestamp = self.date)
                    self.put_entry(entry)
            self.move_file(file)
