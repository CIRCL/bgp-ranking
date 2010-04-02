# -*- coding: utf-8 -*-
from sys import version_info

if version_info < (2,7):
    import urllib2
else:
    import urllib.request, urllib.error
import re
import datetime 

from ip_update import IP_Update


class Dshield_TopIPs(IP_Update):
    url = 'http://www.dshield.org/feeds/topips.txt'
    name = 'Dshield Top IPs'
    date = datetime.date.today() # Dshield doesn't give a date for his TopIPs
# list. So we assume that the list is updated every days
 
    def parse(self):
        """ Parse the list
        """
        topips = urllib2.urlopen(self.url).read()
        self.ips = re.findall('((?:\d{1,3}\.){3}\d{1,3}).*', topips)
