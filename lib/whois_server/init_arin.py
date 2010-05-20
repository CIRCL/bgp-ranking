#!/usr/bin/python

from abstract_init_whois_server import InitWhoisServer
from arin_whois_parser import *

import IPy


class InitARIN(InitWhoisServer):
    
    orgid = '^OrgID:'
    net = '^NetHandle:'
    v6net = '^V6NetHandle:'
    ash = '^ASHandle:'
    poc = '^POCHandle:'
    
    separator = ' '
    pocs_flag = ':pocs'
    orgid_flag = ':orgid'
    parent_flag = ':parent'
    
    keys =  [
        [net    , [] ], 
        [orgid  , [] ], 
        [v6net  , [] ],
        [ash    , [] ],
        [poc    , [] ] ]
        
    archive_name = "arin_db.txt.gz"
    dump_name = "arin_db.txt"

    def __init__(self):
        InitWhoisServer.__init__(self)
    
    def __push_poc(self, parser, redis_key):
       if parser.pochandles:
            # remove duplicate and join each elements separated by 'separator'
           pocs = self.separator.join(list(set(parser.pochandles)))
           self.redis_whois_server.set(redis_key + self.pocs_flag, pocs)
    
    def __push_origid(self, parser, redis_key):
        orgid = parser.orgid[0]
        self.redis_whois_server.set(redis_key + self.orgid_flag, orgid)
        
    def __push_parent(self, parser, redis_key):
        parent = parser.parent
        if parent:
            self.redis_whois_server.set(redis_key + self.parent_flag, parent[0])
    
    # push each values from first_index[0].first_index[1] to first_index[0].255
    def __intermediate_to_last(self, first, main_str = ''):
        intermediate = []
        first = int(first)
        while first <= 255:
            intermediate.append(main_str + str(first))
            first += 1
        return intermediate

    # push each values from last_index[0].0 to last_index[0].last_index[1]
    def __intermediate_from_zero(self, last, main_str = ''):
        intermediate = []
        last = int(last)
        b = 0
        while b <= last:
            intermediate.append(main_str + str(b))
            b += 1
        return intermediate
    
    def __intermediate_between(self, first, last, main_str = ''):
        intermediate = []
        while first <= last:
            intermediate.append(main_str + str(first))
            first += 1
        return intermediate
    
    def __intermediate_sets(self, first_set, last_set, ipv4):
        intermediate = []
        if ipv4:
            first_index = first_set.split('.')
            last_index = last_set.split('.')
            if first_index[0] != last_index[0]:
                # push each values between first and last (first and last excluded) 
                intermediate = self.__intermediate_between(int(first_index[0])+ 1 , int(last_index[0]) - 1)
                # push each values from first_index[0].first_index[1] to first_index[0].255
                intermediate += self.__intermediate_to_last(first_index[1], first_index[0] + '.')
                # push each values from last_index[0].0 to last_index[0].last_index[1]
                intermediate += self.__intermediate_to_last(last_index[1], last_index[0] + '.')
            elif first_index[0] == last_index[0] and first_index[1] == '0' and last_index[1] == '255':
                intermediate.append(first_index[0])
            elif first_index[1] != last_index[1]:
                # push each values between first and last (first and last excluded) 
                intermediate = self.__intermediate_between(int(first_index[1])+ 1 , int(last_index[1]) - 1, first_index[0] + '.')
                # push each values from first_index[0].first_index[1].first_index[2] to first_index[0].first_index[1].255
                intermediate += self.__intermediate_to_last(first_index[2], first_index[0] + '.' + first_index[1] + '.')
                # push each values from last_index[0].last_index[1].0 to last_index[0].last_index[1].last_index[2]
                intermediate += self.__intermediate_to_last(last_index[2], last_index[0] + '.' + last_index[1] + '.')
            elif first_index[1] == last_index[1] and first_index[2] == '0' and last_index[2] == '255':
                intermediate.append(first_index[0] + '.' + first_index[1])
            elif first_index[2] != last_index[2]:
                intermediate = self.__intermediate_between(int(first_index[2]) , int(last_index[2]), first_index[0] + '.' + first_index[1] + '.')
            elif first_index[2] == last_index[2]:
                intermediate.append(first_index[0] + '.' + first_index[1] + '.' + first_index[2])
        # TODO : ipv6.....
        else:
            print('ipv6 not supported for now')     
        return intermediate
                

    def __push_range(self, parser, net_key):
        first = IPy.IP(parser.netrange[0][0])
        last = IPy.IP(parser.netrange[0][1])
        range_key = str(first.int()) + '_' + str(last.int())
        first = str(first)
        last = str(last)
        first_set = re.findall('.*[.]',first)
        if len(first_set) > 0 :
            first_set = first_set[0][:-1]
            last_set = re.findall('.*[.]',last)[0][:-1]
            ipv4 = True
        else:
            first_set = re.findall('.*[:]',first)[0][:-1]
            last_set = re.findall('.*[:]',last)[0][:-1]
            ipv4 = False
        intermediate_sets = []
        intermediate_sets = self.__intermediate_sets(first_set, last_set, ipv4)
        for intermediate_set in intermediate_sets:
            self.redis_whois_server.sadd(intermediate_set, range_key)
        self.redis_whois_server.set(range_key, net_key)

    def push_helper_keys(self, key, redis_key, entry):
       parser = ARINWhois(entry,  key)
       if key == self.orgid:
            self.__push_poc(parser, redis_key)
       elif key == self.net:
           self.__push_poc(parser, redis_key)
           self.__push_origid(parser, redis_key)
           self.__push_parent(parser, redis_key)
           self.__push_range(parser, redis_key)
       elif key == self.v6net:
           self.__push_poc(parser, redis_key)
           self.__push_origid(parser, redis_key)
           self.__push_parent(parser, redis_key)
           self.__push_range(parser, redis_key)
       elif key == self.ash:
           self.__push_poc(parser, redis_key)
           self.__push_origid(parser, redis_key)

if __name__ == "__main__":
    """
    $ time python init_arin.py
    real	22m20.303s
    user	8m48.957s
    sys	1m52.647s
    """
    arin = InitARIN()
    arin.start()
