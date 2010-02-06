#!/usr/bin/python
# -*- coding: utf-8 -*-

from socket import *
import re
import urllib2


risServer = 'riswhois.ripe.net'
whoisPort = 43

ipListURL ='http://www.dshield.org/feeds/topips.txt'
response = urllib2.urlopen(ipListURL)
ipList = response.read()
ips = re.findall('([0-9.]+).+',ipList)

def ASNsofIPs(ips):
  s = socket(AF_INET, SOCK_STREAM)
  s.connect((risServer,whoisPort))
  s.recv(1024)
  ASNs = []
  for ip in ips[:]:
    # Options : http://www.ripe.net/ris/riswhois.html
    s.send('-k -F -M' + ip + ' \n')
    data = s.recv(1024)
    parsedData = re.findall('[0-9./]+',data)
    if (len(parsedData) >= 2):
      ASNs.append(parsedData[-2])
    else:
      print("bug!! (no associated ASN!) ")
  s.close()
  return ASNs


# Idee => http://stackoverflow.com/questions/885546/how-do-you-calculate-the-greatest-number-of-repetitions-in-a-list
def weightASNs(ASNs):
  group = groupby (ASNs)
  result = []
  index = 0
  for k, g in group:
    length = len(list(g))
    result.append((k, length))
    index += length
  sorted(result, key=lambda x:(x[1], x[0]))
  return result


# ------------------------ Old fct ---------------------

# return the ASN and the "best network" of this IP 
def ASNofIP(ip):
  s = socket(AF_INET, SOCK_STREAM)
  s.connect((risServer,whoisPort))
  s.recv(1024)
  s.send('-F ' + ip + ' \n')
  data = s.recv(1024)
  s.close()	
  # The Last ASN is always the better (has to be verified.) 
  return re.findall('[0-9./]+',data)[-2:]