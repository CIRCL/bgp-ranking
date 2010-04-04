# -*- coding: utf-8 -*-
from sys import version_info

if version_info < (2,7):
    import urllib
else:
    import urllib.request, urllib.parse, urllib.error


import re
import datetime 

from utils.ip_update import IP_Update


class Zeustracker_IpBlockList(IP_Update):
    url = 'http://www.abuse.ch/zeustracker/blocklist.php?download=ipblocklist'
    name = 'Zeustracker\'s ipblocklist'
    # Dshield doesn't give a date for his TopIPs list. So we assume that 
    # the list is updated every days
    date = datetime.date.today()
    filename = 'datas/zeus/ipblocklist.' + str(date)
 
    def parse(self):
        """ Parse the list
        """
        urllib.urlretrieve(self.url,self.filename)
        self.ips = re.findall('((?:\d{1,3}\.){3}\d{1,3}).*', open(self.filename).read())
#        print self.ips


if __name__ == "__main__":
    #Just to check the url and print the result (ip addresses)
    d = Zeustracker_IpBlockList()
    d.parse()

