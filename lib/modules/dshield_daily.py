# -*- coding: utf-8 -*-
import re
import time
import datetime
from datetime import datetime
import os

from ip_update import IPUpdate


class DshieldDaily(IPUpdate):
    name = 'Dshield Daily Sources'
    directory = 'dshield/daily/'

    def __init__(self, raw_dir):
        IPUpdate.__init__(self)
        self.directory = os.path.join(raw_dir, self.directory)


    def parse(self):
        """ Parse the list
        """
        self.ips = []
        for file in self.files:
            if not os.path.isdir(file):
                daily = open(file).read()
                self.ips += re.findall('((?:\d{1,3}\.){3}\d{1,3}).*',daily)
                str_date = re.findall('updated (.*)\n', daily)[0]
                self.date = datetime.fromtimestamp(time.mktime(time.strptime(str_date, '%Y-%m-%d %H:%M:%S %Z')))
                self.move_file(file)
