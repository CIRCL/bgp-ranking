# -*- coding: utf-8 -*-

try:
    import urllib.request, urllib.parse, urllib.error
except ImportError:
    import urllib

import re
import time
import os
from datetime import datetime
from .utils.ip_update import IPUpdate


class DshieldDaily(IPUpdate):
    url = 'http://www.dshield.org/feeds/daily_sources'
    name = 'Dshield Daily Sources'
    filename = 'datas/dshield/daily.'

    def parse(self):
        """ Parse the list
        """
        urllib.urlretrieve(self.url, self.filename)
        daily = open(self.filename).read()
        self.ips = re.findall('((?:\d{1,3}\.){3}\d{1,3}).*',daily)
        str_date = re.findall('updated (.*)\n', daily)[0]
        self.date = datetime.fromtimestamp(time.mktime(time.strptime(str_date, '%Y-%m-%d %H:%M:%S %Z')))
        tmp_filename = self.filename + str(self.date).replace(' ','-')
        os.rename(self.filename, tmp_filename)
        self.filename = tmp_filename
        f = open(self.filename,  'w')
        f.write(daily)
        f.close()
