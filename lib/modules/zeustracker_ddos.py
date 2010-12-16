# -*- coding: utf-8 -*-
import re
import os
import datetime 
import dateutil.parser

from modules.abstract_module import AbstractModule


class ZeustrackerDdos(AbstractModule):
    date = datetime.date.today()
    directory = 'zeus/ddos/'
    
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
                date, ip, origin, asn, asn_descr = line.split(' | ')
                if len(ip) == 0:
                    continue
                date = dateutil.parser.parse(date)
                entry = self.prepare_entry(ip = ip, source = self.__class__.__name__, timestamp = date)
                print entry
                #self.put_entry(entry)
            blocklist.close()
            #self.move_file(file)
