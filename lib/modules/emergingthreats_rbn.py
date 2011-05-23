#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    RussianBusinessNetwork IPs list
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    RussianBusinessNetwork IPs list provided by EmergingThreats
    
    .. note::
        See http://doc.emergingthreats.net/bin/view/Main/RussianBusinessNetwork
"""

import IPy

class EmergingThreatsRBN(AbstractModule):

    def __init__(self, raw_dir):
        AbstractModule.__init__(self)
        self.directory = raw_dir

    def parse(self):
        self.date = datetime.date.today()
        for file in self.files:
            rbn = open(file)
            for line in rbn:
                subnet = IPy.IP(line.strip())
                for ip in subnet:
                    entry = self.prepare_entry(ip = ip.strCompressed(), source = self.__class__.__name__, timestamp = self.date)
                    self.put_entry(entry)
            rbn.close()
            self.move_file(file)