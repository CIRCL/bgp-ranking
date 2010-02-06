#!/usr/bin/python

from socket import *
import re


risServer = 'riswhois.ripe.net'
whoisPort = 43


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







