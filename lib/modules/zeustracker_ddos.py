#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Zeustracker DDoS
    ~~~~~~~~~~~~~~~~

    Zeustracker DDoS list provided by Abuse.ch
"""

import re
import os
import datetime

from modules.abuse_ch import AbuseCh

class ZeustrackerDdos(AbuseCh):
    """
        The subclass of AbuseCh which is used to parse the Zeustracker DDoS list
    """
    directory = 'zeus/ddos/'
    list_type = 2

    def __init__(self, raw_dir):
        AbuseCh.__init__(self, raw_dir)
