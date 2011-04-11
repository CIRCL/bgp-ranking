#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Blocklist.de parser
    ~~~~~~~~~~~~~~~~

    Class used to parse the files provided by blocklist.de
"""

import re
import os
import datetime 

from modules.abstract_module import AbstractModule


class BlocklistDe(AbstractModule):
    """
        Parser
    """

    def __init__(self, raw_dir):
        self.directory = 'blocklist_de/ip/'
        AbstractModule.__init__(self)
        self.directory = os.path.join(raw_dir, self.directory)


    def parse(self):
        """ 
            Parse the list
        """
        self.date = datetime.date.today()
        self.ips = []
        for file in self.files:
            daily = open(file)
            for line in daily:
                ip = re.findall('((?:\d{1,3}\.){3}\d{1,3})[\s].*',line)
                if len(ip) == 0:
                    continue
                entry = self.prepare_entry(ip = ip[0], source = self.__class__.__name__, timestamp = self.date)
                self.put_entry(entry)
            daily.close()
            self.move_file(file)
