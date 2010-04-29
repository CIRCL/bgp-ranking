# -*- coding: utf-8 -*-

import re
import time
import os
from datetime import datetime
from .utils.ip_update import IPUpdate
import glob


class DshieldDaily(IPUpdate):
    name = 'Dshield Daily Sources'
    directory = 'datas/dshield/topips/'

    def parse(self):
        """ Parse the list
        """
        self.ips = []
        for file in  glob.glob( os.path.join(self.directory, '*.*') ):
            daily = open(file)
            self.ips.append(re.findall('((?:\d{1,3}\.){3}\d{1,3}).*',daily.read()))
            str_date = re.findall('updated (.*)\n', daily.read())[0]
            self.date = datetime.fromtimestamp(time.mktime(time.strptime(str_date, '%Y-%m-%d %H:%M:%S %Z')))
            new_filename = self.directory + 'old/' + str(self.date).replace(' ','-')
            daily.close()
            os.rename(file, new_filename)
