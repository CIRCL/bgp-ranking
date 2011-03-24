#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    sshbl parser
    ~~~~~~~~~~~~~~~~~~~~

    Class used to parse the files provided by sshbl
"""

import re
import os
import datetime 
from datetime import datetime, date
from modules.abstract_module import AbstractModule


class SshblBase(AbstractModule):
    """
        Parser
    """
    
    def __init__(self, raw_dir):
        # Dshield doesn't give a date for his TopIPs list. So we assume that 
        # the list is updated every days
        self.directory = 'sshbl/base/'
        AbstractModule.__init__(self)
        self.directory = os.path.join(raw_dir, self.directory)
 
    def parse(self):
        """ 
            Parse the list
        """
        self.date = date.today()
        self.ips = []
        for file in self.files:
            daily = open(file)
            for line in daily:
                if line[0] != '#':
                    splitted = line.split()
                    ip = splitted[0]
                    date = datetime.utcfromtimestamp(int(splitted[1]))
                    if len(ip) == 0:
                        continue
                    entry = self.prepare_entry(ip = ip, source = self.__class__.__name__, timestamp = date)
                    self.put_entry(entry)
            daily.close()
            self.move_file(file)
