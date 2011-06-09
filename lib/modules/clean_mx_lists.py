#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Clean MX Lists
    ~~~~~~~~~~~~~~

    All the lists provided by Clean MX
"""

from modules.clean_mx import AbuseCh

class CleanMXMalwares(CleanMXDefault):
    """
        CleanMX Malwares list provided by Clean MX
    """

    def __init__(self, raw_dir):
        CleanMXDefault.__init__(self, raw_dir)

class CleanMXPhishing(CleanMXDefault):
    """
        CleanMX Phishing list provided by Clean MX
    """

    def __init__(self, raw_dir):
        CleanMXDefault.__init__(self, raw_dir)

class CleanMXPortals(CleanMXDefault):
    """
        CleanMX Portals list provided by Clean MX
    """

    def __init__(self, raw_dir):
        CleanMXDefault.__init__(self, raw_dir)
