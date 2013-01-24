#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    nothink parser
    ~~~~~~~~~~~~~~

    Class used to parse the daily files provided by nothink.org
"""

import re
import dateutil.parser
from helper import new_entry


def parser(filename, listname, date):
    try:
        date = dateutil.parser.parse(re.findall('# Generated (.*)\n',
            open(filename, 'r').read())[0])
    except:
        pass
    with open(filename, 'r') as f :
        for line in f:
            ip = re.findall('((?:\d{1,3}\.){3}\d{1,3}).*',line)
            if len(ip) == 0:
                continue
            new_entry(ip = ip[0], source = listname, timestamp = date)
    return date
