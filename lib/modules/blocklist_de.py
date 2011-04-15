#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Blocklist.de parser
    ~~~~~~~~~~~~~~~~~~~

    Class used to parse the files provided by blocklist.de
"""

class BlocklistDe(AbstractModuleDefault):
    """
        Parser
    """

    def __init__(self, raw_dir):
        self.directory = 'blocklist_de/ip/'
        AbstractModuleDefault.__init__(self)
