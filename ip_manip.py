# -*- coding: utf-8 -*-
# Python 2.6 need an external module : netaddr => http://code.google.com/p/netaddr/
# Python 2.7 and Python 3.* have already a module : ipaddr


from sys import version_info
if version_info < (2,7):
  
  from netaddr import IPAddress, IPNetwork

  def ip_in_network(ip,network):
    """ return true if the ip is in the network 
    """
    return IPAddress(ip) in IPNetwork(network)

else:
# TODO ipaddr exists ? => http://docs.python.org/dev/py3k/library/ipaddr.html
  
  from ipaddr import IP
  
  def ip_in_network(ip,network):
    return IP(ip) in IP(network)