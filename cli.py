# -*- coding: utf-8 -*-

from models import *


def list_ASNs():
  return ASNs.query.order_by(ASNs.asn).all()
  
def list_ASNs_descriptions():
  return ASNs_descriptions.query.order_by(ASNs_descriptions.asn_asn).all()

def list_IPs():
  return IPs.query.order_by(IPs.ip).all()

def list_IPs_descriptions():
  return IPs_descriptions.query.order_by(IPs_descriptions.ip_ip).all()

def ASN_descriptions(asn):
  return ASNs_descriptions.query.filter_by(asn=ASNs.query.filter_by(asn=asn).first()).all()
  
def IP_of_ASN(asn):
  descs = ASN_descriptions(asn)
  ips = []
  for desc in descs:
    ips.append(IPs_descriptions.query.filter_by(asn=desc).all())
  return ips 

def display_IPs_by_AS(asns):
  for asn in asns:
    print(asn)
    for ip in asn.ips:
      print(ip)

from cli import *