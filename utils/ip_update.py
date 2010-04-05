# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from .utils.models import *


class IPUpdate ():
    """
    Abstract class which update the databases 'IPs' and 'IPsDescriptions'
    """
    __metaclass__ = ABCMeta
  
    @abstractmethod
    def parse(self):
        """
        Abstract method which has to be implemented in each module: 
          the method must at least extract the IPs of the raw data 
          and initialize a list named ips. 
          The class must also define a variable called date. It is the date 
          of creation of the list. If this date is unknown, it should be 
          set to 'today' like this : 
            date = datetime.date.today()
        """
        pass
    
    def update(self):
        """
        Update the databases 'IPs' and 'IPsDescriptions'.
        ATTENTION: it will *fail* if self.date and self.ips are not definded!
        """
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
