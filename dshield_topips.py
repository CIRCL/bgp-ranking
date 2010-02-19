# -*- coding: utf-8 -*-
import urllib2
import re

from models import *

list_url  = 'http://www.dshield.org/feeds/topips.txt'
list_name_str = 'Dshield Top IPs'


topips = urllib2.urlopen(list_url).read()
ips = re.findall('([0-9.]+).+',topips)

for ip_t in ips:
  current_ip = IPs.query.filter_by(ip=ip_t).all()
  if not current_ip:
    current_ip = IPs(ip=ip_t)
  IPs_descriptions(ip=current_ip, list_name=list_name_str)
  
session.commit()
