#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    CleanMX parser
    ~~~~~~~~~~~~~~

    The default parser of CleanMX lists
"""

import datetime
from xml.etree import cElementTree

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
            for event, elem in cElementTree.iterparse(file):
                # FIXME ensure it is correct
                if elem.tag == "ip" or elem.tag == "review":
                    ip = elem.text
                    if ip is None or len(ip) == 0:
                        continue
                    entry = self.prepare_entry(ip = ip, source = self.__class__.__name__, timestamp = self.date)
                    self.put_entry(entry)
            self.move_file(file)
