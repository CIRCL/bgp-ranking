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
    
    separator = '%'
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
           l = list(set(parser.pochandles))
           pocs = self.separator.join(list(set(parser.pochandles)))
            # remove duplicate and join each elements separated by 'separator'
           self.redis_whois_server.set(redis_key + self.pocs_flag, pocs)
    
    def __push_origid(self, parser, redis_key):
        orgid = parser.orgid[0]
        self.redis_whois_server.set(redis_key + self.orgid_flag, orgid)
        
    def __push_parent(self, parser, redis_key):
        parent = parser.parent[0]
        if parent:
            self.redis_whois_server.set(redis_key + self.parent_flag, parent)

    def __push_networkv4(self, parser, redis_key):
        netrange = parser.netrange[0]
        try:
            network = IPy.IP(netrange)
            self.redis_whois_server.set(network, redis_key)
        except ValueError:
            print (netrange)

    # IPy doesn't support "first-last notation" for IPv6: 
    # IPy.IP('2607:F3D0:001A:0700:0000:0000:0000:0000 - 2607:F3D0:001A:07FF:FFFF:FFFF:FFFF:FFFF')
    def __push_networkv6(self, parser, redis_key):
        first_ip = parser.netrange[0].split(' ')[0]
        self.redis_whois_server.set(first_ip, redis_key)

    def push_helper_keys(self, key, redis_key, entry):
       parser = ARINWhois(entry,  key)
       try:
           if key == self.orgid:
                self.__push_poc(parser, redis_key)
           elif key == self.net:
               self.__push_poc(parser, redis_key)
               self.__push_origid(parser, redis_key)
               self.__push_parent(parser, redis_key)
               self.__push_networkv4(parser, redis_key)
           elif key == self.v6net:
               self.__push_poc(parser, redis_key)
               self.__push_origid(parser, redis_key)
               self.__push_parent(parser, redis_key)
               self.__push_networkv6(parser, redis_key)
           elif key == self.ash:
               self.__push_poc(parser, redis_key)
               self.__push_origid(parser, redis_key)
       except AttributeError:
           print(parser)

if __name__ == "__main__":
    arin = InitARIN()
    arin.start()
