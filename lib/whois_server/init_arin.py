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

    def __push_range(self, parser, net_key):
        first = IPy.IP(parser.netrange[0][0])
        last = IPy.IP(parser.netrange[0][1])
        if first.version() == 4:
            ipv4 = True
        else:
            ipv4 = False
        self.push_range(first, last, net_key, ipv4)


if __name__ == "__main__":
    """
    $ time python init_arin.py 

    real	32m46.930s
    user	12m42.908s
    sys	2m14.784s

    12197608 keys
    """
    arin = InitARIN()
    arin.start()
