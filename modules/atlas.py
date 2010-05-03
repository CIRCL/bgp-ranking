# -*- coding: utf-8 -*-


import re
import time
import os
import glob
import csv

from datetime import datetime
import dateutil.parser
from utils.ip_update import IPUpdate
from xml.dom import minidom

class Atlas(IPUpdate):
    name = 'Atlas'
    directory = 'datas/atlas/'
    
    def __init__(self):
        IPUpdate.__init__(self)
        self.module_type = 2

    def parse(self):
        """ Parse the list
        """
        self.ips = []
        for file in  glob.glob( os.path.join(self.directory, '*') ):
            if not os.path.isdir(file):
                parse = minidom.parse(file)
                self.date = parse.getElementsByTagName('updated')[0].firstChild.data
                values = self.extract_from_xml(parse)
                for value in values:
                    self.ips.append(value)
                self.move_file(file)


    def parse_entry(self,  entry):
        """
        entry: 
        0. ip
        1. date of the report
        2. attack
        3. url for more informations, coverage, category of the attack 
        """
        toReturn = []
        title = entry.getElementsByTagName('title')[0].firstChild.data.split(' | ')
        toReturn.append(title[1])
        toReturn.append(dateutil.parser.parse(entry.getElementsByTagName('updated')[0].firstChild.data))
        toReturn.append(title[0])
        url = entry.getElementsByTagName('id')[0].firstChild.data
        coverage = entry.getElementsByTagName('dc:coverage')[0].firstChild.data
        category_xml_values = entry.getElementsByTagName('category')[0].attributes.values()
        category = category_xml_values[0].value + ' - ' + category_xml_values[2].value
        toReturn.append(url + ', ' + coverage + ', ' + category)
        return toReturn
    
    def extract_from_xml(self, xmldoc):
        entries = xmldoc.getElementsByTagName('entry')
        extracted_values = []
        for entry in entries:
            extracted_values.append(self.parse_entry(entry))
        return extracted_values
