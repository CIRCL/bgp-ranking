#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Main Class for all the modules of Shadowserver
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    It provides helpers to the modules parsing the datasets of Shadowserver
    
    .. note::
        the only difference between the three modules is the position of the fields...
"""

import re
import time
import os
import glob
import csv
from abc import ABCMeta, abstractmethod

import datetime
from modules.abstract_module import AbstractModule

class Shadowserver(AbstractModule):
    """
        Super class used for all shadowserver reports: the subclass has only to define 
         - a unique name 
         - a directory to watch
         - a line parser which return a table : [ip, date, infection, rest of the line]
    """
    
    __metaclass__ = ABCMeta    
    @abstractmethod
    def parse_line(self):
        """
            Abstract method, parse a line of the csv file. 
            The only difference between all the sub-classes is the place of the infections type 
        """
        pass
    
    def __init__(self):
        AbstractModule.__init__(self)

    def parse(self):
        """ 
            Parse the list
        """
        self.date = datetime.date.today()
        self.ips = []
        for file in self.files:
            reader = csv.reader(open(file), delimiter=',')
            reader.next()
            for row in reader:
                value = self.parse_line(row)
                entry = self.prepare_entry(ip = value[0], date = value[1], infection = value[2], raw = value[3], source = self.__class__.__name__)
                self.put_entry(entry)
            self.move_file(file)
