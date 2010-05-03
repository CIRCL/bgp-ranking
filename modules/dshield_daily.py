# -*- coding: utf-8 -*-
import re
import time
import datetime
from datetime import datetime
import os
import glob

from utils.ip_update import IPUpdate


class DshieldDaily(IPUpdate):
    name = 'Dshield Daily Sources'
    directory = 'datas/dshield/daily/'

    def parse(self):
        """ Parse the list
        """
        self.ips = []
        for file in  glob.glob( os.path.join(self.directory, '*') ):
            if not os.path.isdir(file):
                daily = open(file).read()
                self.ips += re.findall('((?:\d{1,3}\.){3}\d{1,3}).*',daily)
                str_date = re.findall('updated (.*)\n', daily)[0]
                self.date = datetime.fromtimestamp(time.mktime(time.strptime(str_date, '%Y-%m-%d %H:%M:%S %Z')))
                self.move_file(file)
