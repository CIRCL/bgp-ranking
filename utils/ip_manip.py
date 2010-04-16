# -*- coding: utf-8 -*-
# Python 2.6 need an external module :
#     netaddr => http://code.google.com/p/netaddr/
# Python 2.7 and Python 3.* have already a module : ipaddr

from sys import version_info

if version_info < (2,7):
  
    import IPy

    def ip_in_network(ip, network):
        """ return true if the ip is in the network 
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


else:
# TODO ipaddr exists ? => http://docs.python.org/dev/py3k/library/ipaddr.html
  
    from ipaddr import IP
  
    def ip_in_network(ip, network):
        return IP(ip) in IP(network)
