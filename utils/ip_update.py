# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from .utils.models import *


class IPUpdate ():
    __metaclass__ = ABCMeta
  
    @abstractmethod
    def parse(self):
        pass
    
    def update(self):
        self.parse()
        for ip in self.ips:
            IP = IPs.query.get(str(ip))
            if not IP:
                IP = IPs(ip=str(ip))
            desc = IPsDescriptions.query.filter_by(ip=IP, \
                   list_name=str(self.name), list_date=self.date).all()
            if not desc:
                IPsDescriptions(ip=IP, \
                list_name=str(self.name), list_date=self.date)
        session.commit()
