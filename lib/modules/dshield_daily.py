# -*- coding: utf-8 -*-
import re
import time
import datetime
from datetime import datetime
import dateutil.parser
import os

from adstract_module import AbstractModule


class DshieldDaily(AbstractModule):
    directory = 'dshield/daily/'
    
    key_ip = ':ip'
    key_src = ':source'
    key_tstamp = ':timestamp'

    def __init__(self, raw_dir):
        IPUpdate.__init__(self)
        self.directory = os.path.join(raw_dir, self.directory)


    def parse(self):
        """ Parse the list
        """
        self.ips = []
        for file in self.files:
            daily = open(file)
            date = dateutil.parser.parse(re.findall('updated (.*)\n', daily.read())[0])
            for line in daily:
                entry[key_ip] = re.findall('((?:\d{1,3}\.){3}\d{1,3}).*',daily)[0]
                entry[key_src] = self.__class__.__name__
                entry[key_tstamp] = date
                self.put_entry(entry)
            daily.close()
            self.move_file(file)
