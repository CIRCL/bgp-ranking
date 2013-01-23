#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    sshbl parser
    ~~~~~~~~~~~~

    Class used to parse the files provided by sshbl
"""

from helper import new_entry

def parser(filename, listname, date):
    with open(filename, 'r') as f:
        for line in f:
            if line[0] != '#':
                ip = line.strip()
                if len(ip) == 0:
                    continue
                new_entry(ip = ip, source = listname, timestamp = date)
    return date
