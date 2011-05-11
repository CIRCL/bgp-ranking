#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Amada IPblocklist
    ~~~~~~~~~~~~~~~~~

    Amada IPblocklist provided by Abuse.ch
    
    .. note::
        the type of the infection is available in the list but 
        not saved by the module
        
        FIXME: save it? 
"""

import re
import os
import datetime 

from modules.abuse_ch import AbuseCh



class AmadaIpBlockList(AbuseCh):
    """
        The subclass of AbuseCh which is used to parse the Amada IPblocklist
    """
    directory = 'amada/ipblocklist/'
    list_type = 1

    def __init__(self, raw_dir):
        AbuseCh.__init__(self, raw_dir)
