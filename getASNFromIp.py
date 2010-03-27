#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import re
import time
from socket import *
from itertools import groupby
from threading import Thread

from whoisParser import WhoisEntry

ipListURL ='http://www.dshield.org/feeds/topips.txt'
response = urllib2.urlopen(ipListURL)
ipList = response.read()

risServer = 'riswhois.ripe.net'
whoisPort = 43
threadsNumber = 10


#ipList = open('topips.txt','r').read()



class threaded(Thread):

    def __init__ (self,ips):
        Thread.__init__(self)
        self.ips = ips
        self.datas = []

    def run(self):
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((risServer,whoisPort))
        s.recv(1024)
        for ip in self.ips[:]:
            # Options : http://www.ripe.net/ris/riswhois.html
            s.send('-k -M ' + ip + ' \n')
            self.datas.append(s.recv(1024))
        s.close


class Ranking(object):
    """ Rank the IPs by AS
    """
    ASNsHash = {}
    ASNs = []
    noASN = []
    ASNsOrdered = []
    ips = []

    def __init__(self,ipList):
        self.ips = re.findall('([0-9.]+).+', ipList)
			  #([0-9.]*)\s.*
        self.ips = list(set(self.ips))

    def ASNsofIPs(self):
        """ Get informations on the AS of each IP 
        """
        IPnumber = len(self.ips)
        IPrange = IPnumber / threadsNumber
        threadList = []
        begin = time.time()
        index = 0;
        while index < IPnumber:
            current = threaded(self.ips[index:index+IPrange])
            threadList.append(current)
            current.start()
            index += IPrange

        datas = []
        for thread in threadList:
            thread.join()
            datas.extend(thread.datas)

        for data in datas[:]:
          whois = WhoisEntry(data)
          if whois.origin:
              self.ASNsHash[int(whois.origin)] = whois
              self.ASNs.append(int(whois.origin))
        print(time.time() - begin)
        self.ASNs.sort()

      # Original idea => http://stackoverflow.com/questions/885546/how
      # -do-you-calculate-the-greatest-number-of-repetitions-in-a-list
    def weightASNs(self):
        """ Rank the ASN and put the description into the list
        """
        group = groupby(self.ASNs)
        index = 0
        for k, g in group:
            length = len(list(g))
            self.ASNsOrdered.append((k, length, self.ASNsHash[k].description))
            index += length
        self.ASNsOrdered = sorted(self.ASNsOrdered, key=lambda x:(x[1], \
x[2], x[0]))

