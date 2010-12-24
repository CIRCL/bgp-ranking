# -*- coding: utf-8 -*-
import re
import os
import datetime 

from modules.abuse_ch import AbuseCh

class ZeustrackerIpBlockList(AbuseCh):
    directory = 'zeus/ipblocklist/'
    list_type = 1

    def __init__(self, raw_dir):
        AbuseCh.__init__(self, raw_dir)
        self.class_name = self.__class__.__name__