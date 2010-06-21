# -*- coding: utf-8 -*-
import re
import time
import datetime
from datetime import datetime
import os

from ip_update import IPUpdate
import dateutil.parser


class Abusix(IPUpdate):
    name = self.__class__.__name__
    directory = 'abusix/'

    def __init__(self, raw_dir):
        IPUpdate.__init__(self)
        self.module_type = 2
        self.directory = os.path.join(raw_dir, self.directory)


    def parse(self):
        """ Parse the list
        """
        self.ips = []
        for file in self.files:
            if not os.path.isdir(file):
                text = open(file).read()
                type = re.findall('Feedback-Type:[\s]*([^\r\n]*)', text)[0]
                user_agent = re.findall('User-Agent:[\s]*([^\n]*)', text)[0]
                ip = re.findall('Source-IP:[\s]*([^\n]*)', text)[0]
                self.date = dateutil.parser.parse(re.findall('Received-Date:[\s]*([^\n]*)', text)[0])
                version = re.findall('Version:[\s]*([^\n]*)', text)[0]
                self.ips.append([ip, self.date, type, str(user_agent) + ', ' + str(version)])
                self.move_file(file)
