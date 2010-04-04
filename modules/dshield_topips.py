# -*- coding: utf-8 -*-
from sys import version_info

if version_info < (2,7):
    import urllib
else:
    import urllib.request, urllib.parse, urllib.error
    
    
import re
import datetime 

from utils.ip_update import IP_Update


class Dshield_TopIPs(IP_Update):
    name = 'Dshield Top IPs'
    url = 'http://www.dshield.org/feeds/topips.txt'
    # Dshield doesn't give a date for his TopIPs list. So we assume that 
    # the list is updated every days
    date = datetime.date.today()
    filename = 'datas/dshield/topips.' + str(date)
 
    def parse(self):
        """ Parse the list
        """
        urllib.urlretrieve(self.url, self.filename)
        self.ips = re.findall('((?:\d{1,3}\.){3}\d{1,3}).*', open(self.filename).read())
