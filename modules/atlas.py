# -*- coding: utf-8 -*-


import re
import time
import os
import glob
import csv

from datetime import datetime
import dateutil.parser
from utils.ip_update import IPUpdate
import feedparser

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
                rss = feedparser.parse(file)
                self.date = rss['feed']['updated']
                values = self.extract_from_xml(rss)
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
        title = entry['title'].split(' | ')
        toReturn.append(title[1])
        toReturn.append(dateutil.parser.parse(entry['updated']))
        toReturn.append(title[0])
        url = entry['id']
        coverage = entry['dc_coverage']
        category_xml_values = entry['tags'][0]['term']
        category = entry['tags'][0]['term'] + ' - ' + entry['tags'][0]['label']
        toReturn.append(url + ', ' + coverage + ', ' + category)
        return toReturn
    
    def extract_from_xml(self, rss):
        entries = rss['entries']
        extracted_values = []
        for entry in entries:
            extracted_values.append(self.parse_entry(entry))
        return extracted_values
