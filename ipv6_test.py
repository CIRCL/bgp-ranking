# -*- coding: utf-8 -*-

import re
import datetime 

from ip_update import IP_Update


class IPv6_Test(IP_Update):
    url = 'datas/ipv6-test'
    name = 'Test IPv6' 
    date = datetime.date.today()

    def parse(self):
        """ Parse the list
        """
        ipv6 = open(self.url).read()
        self.ips = re.findall('([0-9a-f:]*[0-9a-f]).*\n',ipv6)
