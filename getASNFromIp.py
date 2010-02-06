#!/usr/bin/python

import telnetlib
import re

risServer = 'riswhois.ripe.net'
whoisPort = 43

ipToCheck = '74.125.77.104'

s = socket(AF_INET, SOCK_STREAM)
s.connect((risServer,whoisPort))
s.send('-F ' + ipToCheck + ' \n')
data = s.recv(1024)
s.close()

asn = re.findall('\n[0-9]*[\n](.+)[\t]',data)[0]

print(asn)



