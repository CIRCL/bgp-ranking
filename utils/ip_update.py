# -*- coding: utf-8 -*-

from sqlalchemy.orm import scoped_session, sessionmaker
from abc import ABCMeta, abstractmethod
from models import *

import os

try : 
    from ipaddr import IP
except ImportError:
    import IPy

class IPUpdate ():
    """
    Abstract class which update the databases 'IPs' and 'IPsDescriptions'
    We have different types of modules: 
     1. the module return a list of ips and a date for the whole file (default)
           dshield, zeustracker
               ATTENTION: it will *fail* if self.date and self.ips are not definded!
    
     2. the module is more complex and has a different date for each IP. We want to save the raw datas.
           shadowserver
    """
    def __init__(self):
        self.module_type = 1
        # Set the IP to the same format (no leading 0, dot-decimal notation)
        # if possible, count how many times the IP is present in the file
        self.before_insertion = {
                1 : self.__preinsert_type1, 
                2 : self.__preinsert_type2
            }
        # Insert all the needed informations into the database. 
        # Verify that they are nor already present (based on time/ip...) 
        self.insertion =  {
                1 : self.__insert_type1, 
                2 : self.__insert_type2
            }

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
    
    def __preinsert_type1(self):
        self.ip_addresses = {}
        for ip in self.ips:
            checked = ''
            try:
                checked = str(IPy.IP(ip))
            except :
                print('error with IP:' + ip)
                continue
            current_ip = checked
            if not self.ip_addresses.get(current_ip,  None):
                self.ip_addresses[current_ip] = 1
            else:
                self.ip_addresses[current_ip] += 1
    
    def __insert_type1(self):
        for current_ip, current_times in self.ip_addresses.items():
            IP = IPs.query.get(unicode(current_ip))
            if not IP:
                IP = IPs(ip=unicode(current_ip))
            desc = IPsDescriptions.query.filter_by(ip=IP, list_name=unicode(self.name), list_date=self.date).first()
            if not desc:
                desc = IPsDescriptions(ip=IP, list_name=unicode(self.name), list_date=self.date,  times=current_times)
    
    #  self.ips format : [[ip1,timestamp1,infection1,text1],[ip2,timestamp2,infection2,text2]]
    def __preinsert_type2(self):
        for ip in self.ips:
            checked = ''
            try:
                checked = str(IPy.IP(ip[0]))
            except :
                print('error with IP:' + ip[0])
                continue
            ip[0] = checked
    
    def __insert_type2(self):
        for current_ip, current_timestamp, current_infection, current_text in self.ips:
            IP = IPs.query.get(unicode(current_ip))
            if not IP:
                IP = IPs(ip=unicode(current_ip))
            desc = IPsDescriptions.query.filter_by(ip=IP, list_name=unicode(self.name), list_date=current_timestamp).first()
            if not desc:
                IPsDescriptions(ip=IP, list_name=unicode(self.name), list_date=current_timestamp, \
                                infection=unicode(current_infection), raw_informations=unicode(current_text), times=1)
    
    def update(self):
        """
        Update the databases 'IPs' and 'IPsDescriptions'.
        """
        self.parse()
        self.before_insertion[self.module_type]()
        self.insertion[self.module_type]()
        self.r_session = RankingSession()
        self.r_session.commit()
        self.r_session.close()
        
    def move_file(self, file):
        new_filename = self.directory + 'old/' + str(self.date).replace(' ','-')
        os.rename(file, new_filename)
