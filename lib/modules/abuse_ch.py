#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Main Class for all the modules of Abuse.ch
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    It provides helpers to the modules parsing the datasets of Abuse.ch

    .. note::
        raw_dir might seems useless but it is a parameter because like this,
        we do not have to import the configuration file in the module.
"""

import re
import os
import datetime
import dateutil.parser

from modules.abstract_module import AbstractModule

class AbuseCh(AbstractModule):
    """
        Contains all the function needed by the modules for abuse.ch
    """


    def __init__(self, raw_dir):
        AbstractModule.__init__(self)
        self.directory = raw_dir

    def parse(self):
        """
            Parse the list depending on the type (blocklist or ddos)
            and put the entries into redis
        """
        self.date = datetime.date.today()
        self.ips = []
        for file in self.files:
            blocklist = open(file)
            for line in blocklist:
                if self.list_type == 1:
                    ip = self.line_blocklist(line)
                    date = self.date
                elif self.list_type == 2:
                    ip, date = self.line_ddos(line)
                if ip is None:
                    continue
                entry = self.prepare_entry(ip = ip, source = self.__class__.__name__, timestamp = date)
                self.put_entry(entry)
            blocklist.close()
            self.move_file(file)

    def line_ddos(self, line):
        """
            Parse a ligne of a ddos file
        """
        splitted = line.split(' | ')
        if len(splitted) > 0:
            ip = splitted[1]
            date = dateutil.parser.parse(splitted[0])
            return ip, date
        else:
            return None, None

    def line_blocklist(self, line):
        """
            Parse a ligne of a blocklist file
        """
        ip = re.findall('((?:\d{1,3}\.){3}\d{1,3})',line)
        if len(ip) > 0:
            return ip[0]
        else:
            return None
