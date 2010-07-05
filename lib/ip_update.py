# -*- coding: utf-8 -*-

from sqlalchemy.orm import scoped_session, sessionmaker
from abc import ABCMeta, abstractmethod
from db_models.ranking import *

import os
import glob

import syslog
syslog.openlog('BGP_Ranking_IP_Update', syslog.LOG_PID, syslog.LOG_USER)

import IPy

class IPUpdate ():
    """ 
    Abstract class which update the databases 'IPs' and 'IPsDescriptions'
    We have different types of modules: 
     1. the module return a list of ips and a date for the whole file (default)
           dshield, zeustracker
               ATTENTION: it will *fail* if self.date and self.ips are not definded!
            Format of self.ips : [] / Format of self.date : datetime
    
     2. the module is more complex and has a different date for each IP. We want to save the raw datas.
           shadowserver
           Format of self.ips : [[ip1,timestamp1,infection1,text1],[ip2,timestamp2,infection2,text2]]
    """
    
    def __init__(self):
        """
        Set default module to 1, intialise the switches to select the right functions before the insertion and to insert the data
        """
        self.module_type = 1
        self.before_insertion = {
                1 : self.__preinsert_type1, 
                2 : self.__preinsert_type2
            }
        self.insertion =  {
                1 : self.__insert_type1, 
                2 : self.__insert_type2
            }
        
        self.name = self.__class__.__name__
            
    def __glob_only_files(self):
        allfiles = glob.glob( self.directory + '/*')
        self.files = []
        for file in allfiles:
            if not os.path.isdir(file):
                self.files.append(file)

    __metaclass__ = ABCMeta    
    @abstractmethod
    def parse(self):
        """
        Abstract method which has to be implemented in each module: 
          the method must at least extract the IPs of the raw data and initialize a list named ips. 
          
          If self.module_type == 1, the class must also define a variable called date. 
          It is the date of creation of the list. If this date is unknown, 
          it should be set to 'today' like this : date = datetime.date.today()
        """
        pass
    
    def __preinsert_type1(self):
        """
        Check if the IPs are valid and set them to the same format (no leading 0, dot-decimal notation)
        Count how many times the IP is present in the file
        
        Note: print an error if the IP in invalid.
        """
        self.ip_addresses = {}
        for ip in self.ips:
            checked = ''
            try:
                ip_temp = IPy.IP(ip)
                if ip_temp.iptype() != 'PUBLIC':
                    syslog.syslog(syslog.LOG_ERR, str(ip_temp) + ' is not a PUBLIC IP Address but is ' + ip_temp.iptype())
                    continue
                checked = str(ip_temp)
            except :
                syslog.syslog(syslog.LOG_ERR, 'error with IP:' + ip)
                continue
            if not self.ip_addresses.get(checked,  None):
                self.ip_addresses[checked] = 1
            else:
                self.ip_addresses[checked] += 1
    
    def __insert_type1(self):
        """
        Insert a new IPsDescriptions into the database if the same is not already there
        """
        for current_ip, current_times in self.ip_addresses.items():
            IP = IPs.query.get(unicode(current_ip))
            if not IP:
                IP = IPs(ip=unicode(current_ip))
            desc = IPsDescriptions.query.filter_by(ip=IP, list_name=unicode(self.name), list_date=self.date).first()
            if not desc:
                desc = IPsDescriptions(ip=IP, list_name=unicode(self.name), list_date=self.date, times=current_times)
    
    def __preinsert_type2(self):
        """
        Check if the IPs are valid and set them to the same format (no leading 0, dot-decimal notation)
        Note: print an error if the IP in invalid.
        """
        for ip in self.ips:
            checked = ''
            try:
                ip_temp = IPy.IP(ip[0])
                if ip_temp.iptype() != 'PUBLIC':
                    syslog.syslog(syslog.LOG_ERR, str(ip_temp) + ' is not a PUBLIC IP Address but is ' + ip_temp.iptype())
                    continue
                checked = str(ip_temp)
            except :
                syslog.syslog(syslog.LOG_ERR, 'error with IP:' + ip[0])
                continue
            ip[0] = checked
    
    def __insert_type2(self):
        """
        Insert a new IPsDescriptions into the database if the same is not already there
        """
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
        self.__glob_only_files()
        if len(self.files) > 0:
            self.parse()
            self.before_insertion[self.module_type]()
            self.insertion[self.module_type]()
            self.r_session = RankingSession()
            self.r_session.commit()
            self.r_session.close()
            return True
        else:
            return False
        
    def move_file(self, file):
        """
        Move /from/some/dir/file to /from/some/dir/old/file
        """
        new_filename = os.path.join(self.directory, config.get('fetch_files','old_dir'), str(self.date).replace(' ','-'))
        os.rename(file, new_filename)
