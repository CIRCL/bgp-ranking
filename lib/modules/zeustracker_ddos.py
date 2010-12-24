# -*- coding: utf-8 -*-
import re
import os
import datetime

from modules.abuse_ch import AbuseCh

class ZeustrackerDdos(AbuseCh):
    directory = 'zeus/ddos/'
    class_name = __class__.__name__
    list_type = 2
