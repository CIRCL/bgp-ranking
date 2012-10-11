#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Default parser
    ~~~~~~~~~~~~~~

    This abstract class just extract IP Addresses from a file
"""

import re
import os
import datetime

from modules.abstract_module import AbstractModule


class AbstractModuleDefault(AbstractModule):
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
            daily = open(file)
            for line in daily:
                # TODO: Would also '((?:\d{1,3}\.){3}\d{1,3})' do the job?
                ip = re.findall('((?:\d{1,3}\.){3}\d{1,3})[\s].*',line)
                if len(ip) == 0:
                    continue
                entry = self.prepare_entry(ip = ip[0], source = self.__class__.__name__, timestamp = self.date)
                self.put_entry(entry)
            daily.close()
            self.move_file(file)
