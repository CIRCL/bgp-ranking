#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Blocklist.de parsers
    ~~~~~~~~~~~~~~~~~~~~

    Class used to parse the blocklists provided by blocklist.de
"""

from modules.abstract_module_default import AbstractModuleDefault

class BlocklistDeSsh(AbstractModuleDefault):
    """
        SSH blocklist provided by blocklist.de
    """

    def __init__(self, raw_dir):
        AbstractModuleDefault.__init__(self, raw_dir)

class BlocklistDeMail(AbstractModuleDefault):
    """
        Mail blocklist provided by blocklist.de
    """

    def __init__(self, raw_dir):
        AbstractModuleDefault.__init__(self, raw_dir)

class BlocklistDeApache(AbstractModuleDefault):
    """
        Apache blocklist provided by blocklist.de
    """

    def __init__(self, raw_dir):
        AbstractModuleDefault.__init__(self, raw_dir)

class BlocklistDePop3(AbstractModuleDefault):
    """
        Pop3 blocklist provided by blocklist.de
    """

    def __init__(self, raw_dir):
        AbstractModuleDefault.__init__(self, raw_dir)

class BlocklistDeFtp(AbstractModuleDefault):
    """
        FTP blocklist provided by blocklist.de
    """

    def __init__(self, raw_dir):
        AbstractModuleDefault.__init__(self, raw_dir)
