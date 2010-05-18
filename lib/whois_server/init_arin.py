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
           l = list(set(parser.pochandles))
           pocs = self.separator.join(list(set(parser.pochandles)))
            # remove duplicate and join each elements separated by 'separator'
           self.redis_whois_server.set(redis_key + self.pocs_flag, pocs)
    
    def __push_origid(self, parser, redis_key):
        orgid = parser.orgid[0]
        self.redis_whois_server.set(redis_key + self.orgid_flag, orgid)
        
    def __push_parent(self, parser, redis_key):
        parent = parser.parent
        if parent:
            self.redis_whois_server.set(redis_key + self.parent_flag, parent[0])

    # we cannot push the IP ranges as networks... because they are not always!
    def __push_range(self, parser, redis_key):
        first = IPy.IP(parser.netrange[0][0]).int()
        last = IPy.IP(parser.netrange[0][1]).int()
        self.redis_whois_server.set(first, redis_key)
        self.redis_whois_server.set(last, redis_key)

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
