#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Main Class for all the modules of Abuse.ch
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    It provides helpers to the modules parsing the datasets of Abuse.ch

    .. note::
        raw_dir might seems useless but it is a parameter because like this,
        we do not have to import the configuration file in the module.
"""

import dateutil.parser
from helper import new_entry

def parser(filename, listname, date):
    """
        Parse the list depending on the type (blocklist or ddos)
        and put the entries into redis
    """
    with open(filename, 'r') as f:
        for line in f:
            splitted = line.split(' | ')
            if len(splitted) > 0:
                ip = splitted[1]
                local_date = dateutil.parser.parse(splitted[0])
                new_entry(ip = ip, source = listname, timestamp = local_date)
        return date

