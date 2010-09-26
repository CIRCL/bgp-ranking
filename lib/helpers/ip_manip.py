#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
FIXME: verify if it is used. 
"""

import IPy

def ip_in_network(ip, network):
    """ 
    Return true if the ip is in the network 
    """
    return IPy.IP(ip) in IPy.IP(network)
    
def smallest_network(networks):
    """
    Find the shortest network of a list
    """
    smallest = networks[0]
    i = 1 
    while i < len(networks):
        if ip_in_network(networks[i].block, smallest.block):
            smallest = networks[i]
        i +=1
    return smallest

def first_ip(network):
    """
    Return the first IP of the network
    """
    return str(IPy.IP(network)[0])
