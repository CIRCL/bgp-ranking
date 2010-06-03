#!/bin/python
# -*- coding: utf-8 -*-

from db_models.ranking import *

from abstract_graf import *

class ASGraf(AbstractGraf):
    
    def prepare_graf(self, descriptions):
        if len(descriptions) == 0:
            return False
        datas = {}
        for desc in descriptions:
            data = datas.get(desc.timestamp.date(), None)
            if data is None:
               datas[desc.timestamp.date()] = len(desc.ips)
            else:
               datas[desc.timestamp.date()] += len(desc.ips)
        self.dates = [ d for d in datas.keys() ]
        self.times = [ t for t in datas.values() ]
        return True



if __name__ == "__main__":    
    def usage():
        print "ip.py ip"
        exit(1)

    if len(sys.argv) < 2:
        usage()

    query = sys.argv[1]
