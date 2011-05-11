#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Zeustracker IPblocklist
    ~~~~~~~~~~~~~~~~~~~~~~~

    Zeustracker IPblocklist provided by Abuse.ch
"""


import re
import os
import datetime 

from modules.abuse_ch import AbuseCh

class ZeustrackerIpBlockList(AbuseCh):
    """
        The subclass of AbuseCh which is used to parse the Zeustracker IPblocklist
    """
    directory = 'zeus/ipblocklist/'
    list_type = 1

    def __init__(self, raw_dir):
        AbuseCh.__init__(self, raw_dir)
