# -*- coding: utf-8 -*-

try:
    import urllib.request, urllib.parse, urllib.error
except ImportError:
    import urllib2

import re
import datetime 

from .utils.ip_update import IPUpdate


class DshieldDaily(IPUpdate):
    url = 'http://www.dshield.org/feeds/daily_sources'
    name = 'Dshield Daily Sources'
    filename = 'datas/dshield/daily.'

    def parse(self):
        """ Parse the list
        """
        daily = urllib2.urlopen(self.url).read()
        self.ips = re.findall('((?:\d{1,3}\.){3}\d{1,3}).*',daily)
        str_date = re.findall('updated (.*)\n', daily)[0]
        self.date = datetime.strptime(str_date, '%Y-%m-%d %H:%M:%S %Z')
        self.filename = self.filename + str(self.date)
        f = open(self.filename)
        f.write(daily)
        f.close()
