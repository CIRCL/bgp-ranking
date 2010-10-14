# -*- coding: utf-8 -*-
import re
import time
import datetime
from datetime import datetime
import os

from modules.abstract_module import AbstractModule
import dateutil.parser


class Abusix(AbstractModule):
    directory = 'abusix/'

    def __init__(self, raw_dir):
        AbstractModule.__init__(self)
        self.directory = os.path.join(raw_dir, self.directory)


    def parse(self):
        """ Parse the list
        """
        self.ips = []
        for file in self.files:
            abusix = file.open().read()
            type = re.findall('Feedback-Type:[\s]*([^\r\n]*)', abusix)[0]
            user_agent = re.findall('User-Agent:[\s]*([^\n]*)', abusix)[0]
            ip = re.findall('Source-IP:[\s]*([^\n]*)', abusix)[0]
            self.date = dateutil.parser.parse(re.findall('Received-Date:[\s]*([^\n]*)', abusix)[0])
            version = re.findall('Version:[\s]*([^\n]*)', abusix)[0]
            entry = self.prepare_entry(ip = ip, source = self.__class__.__name__, \
                                    timestamp = self.date, raw = str(user_agent) + ', ' + str(version))
            self.put_entry(entry)
            file.close()
            self.move_file(file)
