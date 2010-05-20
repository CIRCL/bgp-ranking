#!/usr/bin/python
# Needs redis-py from git! the stable version has a bug in keys()

import IPy
import re

from abstract_whois_query import WhoisQuery

class ARINQuery(WhoisQuery):
    
    contacts = []
    
    def whois_asn(self, query):
        to_return = self.redis_whois_server.get(query)
        if not to_return:
            to_return = 'ASN not found.'
        else:
            to_return += self.__get_orgid_with_contacts(query)
            self.__get_contacts(query)
            contact_datas = self.__get_contacts_datas()
            if contact_datas:
                to_return += contact_datas
        return to_return

    def __get_orgid_with_contacts(self, query):
        to_return = ''
        key = self.redis_whois_server.get(query + ':orgid')
        if key:
            to_return += self.append_value(key)
            self.__get_contacts(key) 
        return to_return
    
    def __get_contacts(self, key):
        keys = self.redis_whois_server.get(key + ':pocs')
        if keys:
            self.contacts += keys.split()
    
    def __get_contacts_datas(self):
        to_return = ''
        if len(self.contacts) > 0:
            self.contacts = list(set(self.contacts))
            for contact in self.contacts:
                to_return += self.append_value(contact)
        return to_return

    def __find_key(self, ip):
        to_return = None
        ranges = None
        key = str(ip)
        while not ranges:
            if self.ipv4 :
                key = re.findall('.*[.]', key)
            else: 
                print('IPv6 not implemented')
                sys.exit(0)
            if len(key) != 0:
               key = key[0][:-1]
            else:
                break
            ranges = self.redis_whois_server.smembers(key)
        
        for range in ranges:
            print range
            splitted = range.split('_')
            print splitted
            ip_int = ip.int()
            print ip_int
            if int(splitted[0]) <= ip_int and int(splitted[1]) >= ip_int:
                to_return = self.redis_whois_server.get(range)
                print to_return
                break
        return to_return



    def whois_ip(self, ip):
        ip = IPy.IP(ip)
        if ip.version() == 4:
            self.ipv4 = True
        key = self.__find_key(ip)
        to_return = ''
        if not key:
            to_return += 'IP not found.'
        else:
            to_return += self.redis_whois_server.get(key)
            to_return += self.__get_orgid_with_contacts(key)
            to_return += self.get_value('parent', key)
            self.__get_contacts(query)
            to_return += self.__get_contacts_datas()
        return to_return
    
if __name__ == "__main__":
    import os 
    import sys
    query_maker = ARINQuery()
    
    def usage():
        print "arin_query.py query"
        exit(1)

    if len(sys.argv) < 2:
        usage()

    query = sys.argv[1]
    ip = None
    try:
        ip = IPy.IP(query)
    except:
        pass


    if ip:
        print(query_maker.whois_ip(ip))
    else:
       print(query_maker.whois_asn(query))
