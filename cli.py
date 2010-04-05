#!/bin/python
# -*- coding: utf-8 -*-

from .utils.models import *
from .cli import *

def list_ASNs():
    return ASNs.query.order_by(ASNs.asn).all()
  
def list_ASNs_descriptions():
    return ASNDescriptions.query.order_by(ASNsDescriptions.asn_asn).all()

def list_IPs():
    return IPs.query.order_by(IPs.ip).all()

def list_IPs_descriptions():
    return IPsDescriptions.query.order_by(IPsDescriptions.ip_ip).all()

def ASN_descriptions(asn):
    return ASNsDescriptions.query.filter_by(\
           asn=ASNs.query.filter_by(asn=asn).first()).all()
  
def IP_of_ASN(asn):
    descs = ASNDescriptions(asn)
    ips = []
    for desc in descs:
        ips.append(IPsDescriptions.query.filter_by(asn=desc).all())
    return ips 

def display_IPs_by_AS(asns):
    for asn in asns:
        print(asn)
        for ip in asn.ips:
            print(ip)
