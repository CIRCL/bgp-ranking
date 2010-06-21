# -*- coding: utf-8 -*-
import re
import datetime 
import os
import glob

from ip_update import IPUpdate


class ZeustrackerIpBlockList(IPUpdate):
    name = self.__class__.__name__
    date = datetime.date.today()
    directory = 'zeus/ipblocklist/'
    
    def __init__(self, raw_dir):
        IPUpdate.__init__(self)
        self.directory = os.path.join(raw_dir, self.directory)
 
    def parse(self):
        """ Parse the list
        """
        self.ips = []
        for file in self.files:
            if not os.path.isdir(file):
                blocklist = open(file)
                self.ips += re.findall('((?:\d{1,3}\.){3}\d{1,3}).*', blocklist.read())
                self.move_file(file)
