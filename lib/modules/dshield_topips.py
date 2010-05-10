# -*- coding: utf-8 -*-
import re
import datetime 
import os
import glob

from ip_update import IPUpdate


class DshieldTopIPs(IPUpdate):
    name = 'Dshield Top IPs'
    # Dshield doesn't give a date for his TopIPs list. So we assume that 
    # the list is updated every days
    date = datetime.date.today()
    directory = 'dshield/topips/'
    
    def __init__(self, raw_dir):
        IPUpdate.__init__(self)
        self.directory = os.path.join(raw_dir, self.directory)
 
    def parse(self):
        """ Parse the list
        """
        self.ips = []
        for file in self.files:
            if not os.path.isdir(file):
                topips = open(file)
                self.ips += re.findall('((?:\d{1,3}\.){3}\d{1,3}).*', topips.read())
                self.move_file(file)
