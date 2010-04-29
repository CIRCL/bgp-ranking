# -*- coding: utf-8 -*-
import re
import datetime 
import os
import glob

from utils.ip_update import IPUpdate


class DshieldTopIPs(IPUpdate):
    name = 'Dshield Top IPs'
    # Dshield doesn't give a date for his TopIPs list. So we assume that 
    # the list is updated every days
    date = datetime.date.today()
    directory = 'datas/dshield/topips/'
 
    def parse(self):
        """ Parse the list
        """
        self.ips = []
        for file in  glob.glob( os.path.join(self.directory, '*') ):
            if not os.path.isdir(file):
                topips = open(file)
                self.ips += re.findall('((?:\d{1,3}\.){3}\d{1,3}).*', topips.read())
                new_filename = self.directory + 'old/' + os.path.basename(file)
                os.rename(file, new_filename)
