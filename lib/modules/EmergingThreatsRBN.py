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
from helper import new_entry

def parser(filename, listname, date):
    with open(filename, 'r') as f:
        for line in f:
            subnet = IPy.IP(line.strip())
            for ip in subnet:
                new_entry(ip = ip.strCompressed(), source = listname,
                        timestamp = date)
    return date
