# -*- coding: utf-8 -*-

import re
import time
import os
import glob
import csv
from abc import ABCMeta, abstractmethod

from datetime import datetime
from ip_update import IPUpdate

class Shadowserver(IPUpdate):
    """
    Super class used for all shadowserver reports: the subclass has only to define 
    - a unique name 
    - a directory to watch
    - a line parser whitch return a table : [ip, date, infection, rest of the line]
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
        """
        Set the type to 2 
        """
        IPUpdate.__init__(self)
        self.module_type = 2

    def parse(self):
        """ Parse the list
        """
        self.ips = []
        for file in  glob.glob( os.path.join(self.directory, '*') ):
            if not os.path.isdir(file):
                reader = csv.reader(open(file), delimiter=',')
                reader.next()
                for row in reader:
                    self.ips.append(self.parse_line(row))
                self.move_file(file)
    
    def move_file(self, file):
        """
        Move the file without changing the name 
        """
        new_filename = self.directory + 'old/' + os.path.basename(file)
        os.rename(file, new_filename)
