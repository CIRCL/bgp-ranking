# -*- coding: utf-8 -*-
import re
import os
import datetime 
from datetime import datetime
from modules.abstract_module import AbstractModule


class SshblBase(AbstractModule):
    # Dshield doesn't give a date for his TopIPs list. So we assume that 
    # the list is updated every days
    date = datetime.date.today()
    directory = 'sshbl/base/'
    
    def __init__(self, raw_dir):
        AbstractModule.__init__(self)
        self.directory = os.path.join(raw_dir, self.directory)
 
    def parse(self):
        """ Parse the list
        """
        self.ips = []
        for file in self.files:
            daily = open(file)
            for line in daily:
                splitted = line.split()
                ip = splitted[0]
                date = datetime.utcfromtimestamp(int(splitted[1]))
                if len(ip) == 0:
                    continue
                entry = self.prepare_entry(ip = ip, source = self.__class__.__name__, timestamp = date)
                self.put_entry(entry)
            daily.close()
            self.move_file(file)
