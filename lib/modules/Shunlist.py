#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    autoshun parser
    ~~~~~~~~~~~~~~

    Class used to parse the files provided by Autoshun
"""

import csv
from helper import new_entry

def parser(filename, listname, date):
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        for line in reader:
            if len(line) < 3:
                continue
            ip = line[0]
            # The timestamp change many times each day.
            # It breaks the ranking
            # date = dateutil.parser.parse(line[1])
            #comment = line[2]
            new_entry(ip = ip, source = listname, timestamp = date)
    return date
