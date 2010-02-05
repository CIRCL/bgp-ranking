#!/usr/bin/python

import telnetlib
import re

risServer = 'www.ris.ripe.net'
whoisPort = 43

ipToCheck = '74.125.77.104'

tn = telnetlib.Telnet(risServer,whoisPort)
tn.write(ipToCheck + "\n")
tn.write("exit\n")

risServerResponse = tn.read_all()

print(risServerResponse)

asn = re.findall('origin:\s*AS?(.+)',risServerResponse)

print(asn)



