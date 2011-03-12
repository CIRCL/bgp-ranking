#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Spyeyetracker DDoS
    ~~~~~~~~~~~~~~~~~~

    Spyeyetracker DDoS list provided by Abuse.ch
"""

import re
import os
import datetime 

from modules.abuse_ch import AbuseCh

class SpyeyetrackerDdos(AbuseCh):
    """
        The subclass of AbuseCh which is used to parse the Spyeyetracker DDoS lists
    """
    directory = 'spyeye/ddos/'
    list_type = 2

    def __init__(self, raw_dir):
        AbuseCh.__init__(self, raw_dir)
        self.class_name = self.__class__.__name__
