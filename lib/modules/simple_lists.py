#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Simples Lists
    ~~~~~~~~~~~~~

    Some other simple lists
"""


from modules.abstract_module_default import AbstractModuleDefault

class URLQuery(AbstractModuleDefault):
    """
        List provided by urlquery.net
    """

    def __init__(self, raw_dir):
        self.directory = 'urlquery/ip/'
        AbstractModuleDefault.__init__(self, raw_dir)

class MalwareDomainListIP(AbstractModuleDefault):
    """
        List provided by malwaredomainlist.com
    """
    
    def __init__(self, raw_dir):
        self.directory = 'malwaredomainlist/ip/'
        AbstractModuleDefault.__init__(self, raw_dir)

class DshieldTopIPs(AbstractModuleDefault):
    """
        Top IPs list provided by DShield
    """
    
    def __init__(self, raw_dir):
        self.directory = 'dshield/topips/'
        AbstractModuleDefault.__init__(self, raw_dir)
