# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from models import *


class IP_Update ():
    __metaclass__ = ABCMeta
  
    @abstractmethod
    def parse(self):
        pass
    
    def update(self):
        self.parse()
        for ip in self.ips:
            IP = IPs.query.get(unicode(ip))
            if not IP:
                IP = IPs(ip=unicode(ip))
            desc = IPs_descriptions.query.filter_by(ip=IP, \
list_name=unicode(self.name), list_date=self.date).all()
            if not desc:
                IPs_descriptions(ip=IP, \
list_name=unicode(self.name), list_date=self.date)
        session.commit()
