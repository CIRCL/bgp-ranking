# -*- coding: utf-8 -*-


import re
import time
import os
import glob
import csv

from datetime import datetime
from utils.ip_update import IPUpdate


class ShadowserverReport(IPUpdate):
    name = 'Shadowserver report'
    directory = 'datas/shadowserver/report/'
    
    def __init__(self):
        IPUpdate.__init__(self)
        self.module_type = 2

    def parse(self):
        """ Parse the list
        """
        self.ips = []
        for file in  glob.glob( os.path.join(self.directory, '*') ):
            if not os.path.isdir(file):
                reader = csv.reader(open(file), delimiter=',')
                reader.next()
                for row in reader:
                    date = datetime.fromtimestamp(time.mktime(time.strptime(row[0], '%Y-%m-%d %H:%M:%S')))
                    full_line =', '.join(row)
                    self.ips.append([row[1], date, full_line])
                new_filename = self.directory + 'old/' + os.path.basename(file)
                os.rename(file, new_filename)
