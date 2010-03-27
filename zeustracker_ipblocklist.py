# -*- coding: utf-8 -*-

import urllib2
import re
import datetime 

from ip_update import IP_Update


class Zeustracker_IpBlockList(IP_Update):
    url = 'http://www.abuse.ch/zeustracker/blocklist.php?download=ipblocklist'
    name = 'Zeustracker\'s ipblocklist'
    date = datetime.date.today() # Zeustracker doesn't give a date for his IPs
# blocklist. So we assume that the list is updated every days
 
    def parse(self):
        """ Parse the list
        """
        ipblocklist = urllib2.urlopen(self.url).read()
        self.ips = re.findall('((?:\d{1,3}\.){3}\d{1,3}).*', ipblocklist)
        print self.ips


if __name__ == "__main__":
    #Just to check the url and print the result (ip addresses)
    d = Zeustracker_IpBlockList()
    d.parse()

