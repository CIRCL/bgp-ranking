# -*- coding: utf-8 -*-
import re
import time
import datetime
from datetime import datetime
import dateutil.parser
import os

from ip_update import IPUpdate


class DshieldDaily(IPUpdate):
    name = self.__class__.__name__
    directory = 'dshield/daily/'

    def __init__(self, raw_dir):
        IPUpdate.__init__(self)
        self.directory = os.path.join(raw_dir, self.directory)


    def parse(self):
        """ Parse the list
        """
        self.ips = []
        for file in self.files:
            if not os.path.isdir(file):
                daily = open(file).read()
                self.ips += re.findall('((?:\d{1,3}\.){3}\d{1,3}).*',daily)
                self.date = dateutil.parser.parse(re.findall('updated (.*)\n', daily)[0])
                self.move_file(file)
