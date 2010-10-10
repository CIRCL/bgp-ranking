# -*- coding: utf-8 -*-
import re
import os
import dateutil.parser

from modules.abstract_module import AbstractModule


class DshieldDaily(AbstractModule):
    directory = 'dshield/daily/'
    
    key_ip = ':ip'
    key_src = ':source'
    key_tstamp = ':timestamp'

    def __init__(self, raw_dir):
        AbstractModule.__init__(self)
        self.directory = os.path.join(raw_dir, self.directory)


    def parse(self):
        """ Parse the list
        """
        self.ips = []
        for file in self.files:
            self.date = dateutil.parser.parse(re.findall('updated (.*)\n', open(file).read())[0])
            daily = open(file)
            for line in daily:
                ip = re.findall('((?:\d{1,3}\.){3}\d{1,3})[\s].*',line)
                if len(ip) == 0:
                    continue
                entry = {}
                entry[self.key_ip] = ip[0]
                entry[self.key_src] = self.__class__.__name__
                entry[self.key_tstamp] = self.date
                self.put_entry(entry)
            daily.close()
            self.move_file(file)
