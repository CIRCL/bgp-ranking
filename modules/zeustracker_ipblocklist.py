# -*- coding: utf-8 -*-
import re
import datetime 
import os
import glob

from utils.ip_update import IPUpdate


class ZeustrackerIpBlockList(IPUpdate):
    name = 'Zeustracker\'s ipblocklist'
    date = datetime.date.today()
    directory = 'datas/zeus/ipblocklist/'
 
    def parse(self):
        """ Parse the list
        """
        self.ips = []
        for file in  glob.glob( os.path.join(self.directory, '*') ):
            if not os.path.isdir(file):
                blocklist = open(file)
                self.ips += re.findall('((?:\d{1,3}\.){3}\d{1,3}).*', blocklist.read())
                self.move_file(file)
