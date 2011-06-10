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
        AbstractModuleDefault.__init__(self, raw_dir)

class MalwareDomainListIP(AbstractModuleDefault):
    """
        List provided by malwaredomainlist.com
    """
    
    def __init__(self, raw_dir):
        AbstractModuleDefault.__init__(self, raw_dir)

class DshieldTopIPs(AbstractModuleDefault):
    """
        Top IPs list provided by DShield
    """
    
    def __init__(self, raw_dir):
        AbstractModuleDefault.__init__(self, raw_dir)

class Sucuri(AbstractModuleDefault):
    """
        IPs list provided by Sucuri
        .. note:
            contains date
    """

    def __init__(self, raw_dir):
        AbstractModuleDefault.__init__(self, raw_dir)

class EmergingThreatsCompromized(AbstractModuleDefault):
    """
        IPs list of compromized hosts provided by EmergingThreats
        .. note:
            contains date
    """

    def __init__(self, raw_dir):
        AbstractModuleDefault.__init__(self, raw_dir)

class MaliciousnetworksFIRE(AbstractModuleDefault):
    """
        IPs list provided by MaliciousNetworks.org
        .. note:
            contains date
    """

    def __init__(self, raw_dir):
        AbstractModuleDefault.__init__(self, raw_dir)

class CIArmy(AbstractModuleDefault):
    """
        IPs list provided by ciarmy.com
    """

    def __init__(self, raw_dir):
        AbstractModuleDefault.__init__(self, raw_dir)
