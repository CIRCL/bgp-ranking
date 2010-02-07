#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
ipListURL ='http://www.dshield.org/feeds/topips.txt'
response = urllib2.urlopen(ipListURL)
ipList = response.read()

from socket import *
import re
from whoisParser import WhoisEntry
from itertools import groupby


#ipList = open('topips.txt','r').read()

class Ranking(object):
  """ Rank the IPs by AS
  """

  risServer = 'riswhois.ripe.net'
  whoisPort = 43
  ASNsHash = {}
  ASNs = []
  noASN = []
  ASNsOrdered = []
  ips = []

  def __init__(self,ipList):
    self.ips = re.findall('([0-9.]+).+',ipList)
			  #([0-9.]*)\s.*
    self.ips = list(set(self.ips))

  def ASNsofIPs(self):
    """ Get informations on the AS of each IP 
    """
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((self.risServer,self.whoisPort))
    s.recv(1024)
    for ip in self.ips[:]:
      # Options : http://www.ripe.net/ris/riswhois.html
      s.send('-k -M ' + ip + ' \n')
      data = s.recv(1024)
      whois = WhoisEntry(data)
      if not whois.origin:
        self.noASN.append(ip)
      else: 
        self.ASNsHash[int(whois.origin)] = whois
        self.ASNs.append(int(whois.origin))
    s.close()
    self.ASNs.sort()

  # Original idea => http://stackoverflow.com/questions/885546/how-do-you-calculate-the-greatest-number-of-repetitions-in-a-list
  def weightASNs(self):
    """ Rank the ASN and put the description into the list
    """
    group = groupby(self.ASNs)
    index = 0
    for k, g in group:
      length = len(list(g))
      self.ASNsOrdered.append((k, length, self.ASNsHash[k].description))
      index += length
    self.ASNsOrdered = sorted(self.ASNsOrdered, key=lambda x:(x[1], x[2], x[0]))

