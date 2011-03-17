#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Spyeyetracker IPblocklist
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Spyeyetracker IPblocklist provided by Abuse.ch
"""

import re
import os
import datetime 

from modules.abuse_ch import AbuseCh

class SpyeyetrackerIpBlockList(AbuseCh):
    """
        The subclass of AbuseCh which is used to parse the Spyeyetracker IPblocklist
    """
    directory = 'spyeye/ipblocklist/'
    list_type = 1

    def __init__(self, raw_dir):
        AbuseCh.__init__(self, raw_dir)
        self.class_name = self.__class__.__name__