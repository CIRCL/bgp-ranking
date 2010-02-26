# -*- coding: utf-8 -*-

from models import *
setup_all()
from whoisParser import WhoisEntry
from ip_manip import ip_in_network

from socket import *

risServer = 'riswhois.ripe.net'
whoisPort = 43
#threadsNumber = 10

def fetch_asns():
  """ Fetch the ASNs
  """
  # get all the IPs_descriptions which don't have asn
  ips_descriptions = IPs_descriptions.query.filter(IPs_descriptions.asn==None).all()
  s = socket(AF_INET, SOCK_STREAM)
  s.connect((risServer,whoisPort))
  s.recv(1024)
  while len(ips_descriptions) > 0:
    description = ips_descriptions.pop()
    s.send('-k -M ' + description.ip.ip + ' \n')
    update_db(description, ips_descriptions, s.recv(1024))
    print(description.ip.ip)
  s.close()
  session.commit()

def update_db(current, ips_descriptions, data):
  """ Update the database with the whois
  """
  whois = WhoisEntry(data)
  current_asn = ASNs.query.get(whois.origin)
  if not current_asn:
    current_asn = ASNs(asn=whois.origin)
  asn_desc = ASNs_descriptions(proprietary=whois.description, ips_block=whois.route, asn=current_asn)
  current.asn = asn_desc
  check_all_ips(asn_desc, ips_descriptions)


def check_all_ips(asn_desc, ips_descriptions):
  """ Check if the ips are in an ip block we already know
  """
  for desc in ips_descriptions:
    if ip_in_network(desc.ip.ip,asn_desc.ips_block):
      desc.asn = asn_desc
      ips_descriptions.remove(desc)