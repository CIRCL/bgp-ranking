#!/usr/bin/python
# -*- coding: utf-8 -*-
# Original Idea :
# =>  http://code.google.com/p/pywhois/source/browse/trunk/pywhois/parser.py

import re

class WhoisEntry(object):
    """Class for parsing a RIS-Whois entry.
    """
    _whois_regs = {
        'route':       '^route[6]?:\s*(.+)',
        'origin':      'origin:\s*AS(.+)',
        'description': 'descr:\s*(.+)',
        'first':       'lastupd-frst:\s*(.+)',
        'last':        'lastupd-last:\s*(.+)',
        'seen-at':     'seen-at:\s*(.+)',
        'rispeers':    'num-rispeers:\s*(.+)',
        'source':      'source:\s*(.+)'
    }

    def __init__(self, text):
        self.text = text

    def __getattr__(self, attr):
        """The first time an attribute is called it will be calculated here.
        The attribute is then set to be accessed directly by subsequent calls.
        """
        whois_reg = self._whois_regs.get(attr)
        if whois_reg:
            value = re.findall(whois_reg, self.text)
            if not value:
                setattr(self, attr, None)
            else:
                setattr(self, attr, value[0])
            return getattr(self, attr)
        else:
            raise KeyError("Unknown attribute: %s" % attr)

    def __str__(self):
        """Print all whois properties of IP
        """
        return '\n'.join('%s: %s' % (attr, str(getattr(self, attr))) for attr\
in self._whois_regs)
