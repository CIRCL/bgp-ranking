# -*- coding: utf-8 -*-
import re
import os
import datetime 
import dateutil.parser

from modules.abstract_module import AbstractModule


class AbuseCh(AbstractModule):
    date = datetime.date.today()
    
    def __init__(self, raw_dir):
        AbstractModule.__init__(self)
        self.directory = os.path.join(raw_dir, self.directory)
 
    def parse(self):
        """ Parse the list
        """
        self.ips = []
        for file in self.files:
            blocklist = open(file)
            for line in blocklist:
                if self.list_type == 1:
                    ip = self.line_blocklist()
                    date = self.date
                elif self.list_type == 2:
                    ip, date = self.line_ddos()
                if ip is None:
                    continue
                entry = self.prepare_entry(ip = ip, source = self.class_name, timestamp = date)
                self.put_entry(entry)
            blocklist.close()
            self.move_file(file)

    def line_ddos(self):
        splitted = line.split(' | ')
        if len(splitted) > 0:
            ip = splitted[1]
            date = dateutil.parser.parse(splitted[0])
            return ip, date
        else:
            return None, None
 
    def line_blocklist(self):
        ip = re.findall('((?:\d{1,3}\.){3}\d{1,3})',line)
        if len(ip) > 0:
            return ip[0]
        else:
            return None
