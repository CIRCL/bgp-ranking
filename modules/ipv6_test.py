# -*- coding: utf-8 -*-

import re
import datetime 

from utils.ip_update import IPUpdate


class IPv6Test(IPUpdate):
    url = 'datas/ipv6-test'
    name = 'Test IPv6' 
    date = datetime.date.today()

    def parse(self):
        """ Parse the list
        """
        ipv6 = open(self.url).read()
        self.ips = re.findall('([0-9a-f:]*[0-9a-f]).*\n',ipv6)
