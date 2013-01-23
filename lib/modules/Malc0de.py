#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    malc0de parser
    ~~~~~~~~~~~~~~

    Class used to parse the daily files provided by DShield
"""

import re
import dateutil.parser
from helper import new_entry


def parser(filename, listname, date):
    try:
        date = dateutil.parser.parse(re.findall('Last updated (.*)\n',
            open(filename, 'r').read())[0])
    except:
        pass
    with open(filename, 'r') as f :
        for line in f:
            ip = re.findall('((?:\d{1,3}\.){3}\d{1,3})[\s].*',line)
            if len(ip) == 0:
                continue
            new_entry(ip = ip[0], source = listname, timestamp = date)
    return date
