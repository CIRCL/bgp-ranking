# -*- coding: utf-8 -*-

import urllib2
import re
import datetime 

from datetime import datetime, date
from ip_update import IP_Update


class Dshield_Daily(IP_Update):
    url = 'http://www.dshield.org/feeds/daily_sources'
    name = 'Dshield Daily Sources' 

    def parse(self):
        """ Parse the list
        """
        daily = urllib2.urlopen(self.url).read()
        self.ips = re.findall('((?:\d{1,3}\.){3}\d{1,3}).*',daily)
        str_date = re.findall('updated (.*)\n', daily)[0]
        self.date = datetime.strptime(str_date, '%Y-%m-%d %H:%M:%S %Z')
