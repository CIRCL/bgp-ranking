# -*- coding: utf-8 -*-

from models import IPs, IPs_descriptions, ASNs, ASNs_descriptions
from whoisParser import WhoisEntry
from ip_manip import ip_in_network

from socket import *

risServer = 'riswhois.ripe.net'
whoisPort = 43
threadsNumber = 10

# get all the IPs_descriptions which don't have asn
ips_descriptions = IPs_descriptions.query.filter(IPs_descriptions.asn==None).all()

s = socket(AF_INET, SOCK_STREAM)
s.connect((risServer,whoisPort))
s.recv(1024)
while ips_descriptions:
  description = ips_descriptions.pop()
  s.send('-k -M ' + description.ip.ip + ' \n')
  update_db(description, ips_descriptions, s.recv(1024))
s.close()
session.commit()

def update_db(current, ips_descriptions, data):
  whois = WhoisEntry(data)
  asn_desc = ASNs_descriptions(proprietary=whois.description, ips_block=whois.route, asn=ASNs(asn=whois.origin))
  current.asn = asn_desc
  check_all_ips(asn_desc, ips_descriptions)
  
# check if the ips are in an ip block we already know
def check_all_ips(asn_desc, ips_descriptions):
  for desc in ips_descriptions:
    if ip_in_network(desc.ip.ip,asn_desc.ips_block):
      desc.asn = asn_desc
      ips_descriptions.remove(desc)
      
      
