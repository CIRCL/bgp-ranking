#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Abuse.ch Lists
    ~~~~~~~~~~~~~~

    All the lists provided by Abuse.ch
"""

from modules.abuse_ch import AbuseCh

class ZeustrackerIpBlockList(AbuseCh):
    """
        Zeustracker IPblocklist provided by Abuse.ch
    """

    def __init__(self, raw_dir):
        self.list_type = 1
        AbuseCh.__init__(self, raw_dir)

class SpyeyetrackerIpBlockList(AbuseCh):
    """
        Spyeyetracker IPblocklist provided by Abuse.ch
    """

    def __init__(self, raw_dir):
        self.list_type = 1
        AbuseCh.__init__(self, raw_dir)

class PalevotrackerIpBlockList(AbuseCh):
    """
        Palevotracker IPblocklist provided by Abuse.ch
    """

    def __init__(self, raw_dir):
        self.list_type = 1
        AbuseCh.__init__(self, raw_dir)

class SpyeyetrackerDdos(AbuseCh):
    """
        Spyeyetracker DDoS list provided by Abuse.ch
    """

    def __init__(self, raw_dir):
        self.list_type = 2
        AbuseCh.__init__(self, raw_dir)

class ZeustrackerDdos(AbuseCh):
    """
        Zeustracker DDoS list provided by Abuse.ch
    """

    def __init__(self, raw_dir):
        self.list_type = 2
        AbuseCh.__init__(self, raw_dir)
