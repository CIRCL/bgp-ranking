#!/usr/bin/python

from abstract_init_whois_server import InitWhoisServer
from ripe_whois_parser import *
import filecmp
import shutil

import os
import redis
import re
import IPy

class InitRIPE(InitWhoisServer):
    inetnum = '^inetnum:'
    inet6num = '^inet6num:'
    person = '^person:'
    role = '^role:'
    domain = '^domain:'
    aut_num = '^aut-num:'
    route = '^route:'
    route6 = '^route6:'
    as_set = '^as-set:'
    rtr_set = '^rtr-set:'
    route_set = '^route-set:'
    poetic_form = '^poetic-form:'
    poem ='^poem:' 
    peering_set ='^peering-set:'
    limerick ='^limerick:'
    key_cert = '^key-cert:'
    inet_rtr ='^inet-rtr:'
    filter_set ='^filter-set:'
    irt = '^irt:'
    mntner = '^mntner:' 
    organisation = '^organisation:'
    as_block = '^as-block:'
    
    mntners_flag = ':mntners'
    persons_flag = ':persons'
    aut_nums_flag = ':autnum'
    
    origin_flag = ':origin'
    irt_flag = ':irt'    

    keys =  {
         inetnum       : [] ,
         domain        : [] ,
         inet6num      : [] ,
         aut_num       : [] ,
         route         : [] ,
         route6        : [] ,
         as_block      : [] , # Not used for now.
         as_set        : [] ,
         rtr_set       : [] ,
         route_set     : [] ,
         poetic_form   : [] ,
         poem          : [] ,
         peering_set   : [] ,
         limerick      : [] ,
         key_cert      : [] ,
         inet_rtr      : [] ,
         filter_set    : [] , 
        #Dummy
         irt           : [] , 
         mntner        : [] , 
         organisation  : [] , 
         person        : [] , 
         role          : []  }

    nic_keys = [ person , role ]    

    archive_name = "ripe.db.dummy.gz"
    dump_name = "testing"
    serial = "RIPE.CURRENTSERIAL"

    def __init__(self):
        InitWhoisServer.__init__(self)
        self.serial = os.path.join(self.whois_db,self.serial)
        self.last_parsed_serial = os.path.join(self.whois_db, self.serial + "_last")

    def new_file(self):
        if os.path.exists(last_parsed_serial) and filecmp.cmp(serial, last_parsed_serial):
            return False
        return True

    def  copy_serial(self):
        shutil.copy(self.serial,self.last_parsed_serial)
    

    def push_list_at_key(self, mylist, redis_key, flag, subkey):
        mylist = list(set(mylist))
        main_key = redis_key + flag
        for elt in mylist:
            self.redis_whois_server.sadd(main_key, elt)
            self.redis_whois_server.sadd(elt + subkey, redis_key)

    def push_mntners(self, parser, redis_key, subkey):
        mntners = []
        mnt_by = parser.mnt_by
        mnt_lower = parser.mnt_lower
        mnt_routes = parser.mnt_routes
        mnt_ref = parser.mnt_ref
        if mnt_by is not None:
            mntners.extend(mnt_by)
        if mnt_lower is not None:
            mntners.extend(mnt_lower)
        if mnt_routes is not None:
            mntners.extend(mnt_routes)
        if mnt_ref is not None:
            mntners.extend(mnt_ref)
        print mntners
        self.push_list_at_key(mntners, redis_key, self.mntners_flag, subkey)

    def push_persons(self, parser, redis_key, subkey):
        persons = []
        tech_c = parser.tech_c
        admin_c = parser.admin_c
        author = parser.author
        zone_c = parser.zone_c
        if tech_c is not None:
            persons.extend(tech_c)
        if admin_c is not None:
            persons.extend(admin_c)
        if author is not None:
            persons.extend(author)
        if zone_c is not None:
            persons.extend(zone_c)
        print parser
        print persons
        self.push_list_at_key(persons, redis_key, self.persons_flag, subkey)
    
    def push_origin(self, parser, redis_key):
        origin = parser.origin
        if origin is not None:
            self.redis_whois_server.sadd(redis_key + self.origin_flag, origin[0])
    
    def push_irt(self, parser, redis_key):
        irt = parser.mnt_irt
        if irt is not None:
            self.redis_whois_server.sadd(redis_key + self.irt_flag, irt[0])
    
    def push_diverses_aut_num(self, parser, redis_key, subkey):
        aut_nums = []
        members = parser.members
        local_as = parser.local_as
        if members is not None:
            aut_nums.extend(members)
        if local_as is not None:
            aut_nums.extend(local_as)
        self.push_list_at_key(aut_nums, redis_key, self.aut_nums_flag, subkey)

    def push_helper_keys(self, key, redis_key, entry):
        parser = RIPEWhois(entry,  key)
        if key == self.inetnum:
            self.ipv4 = True
            self.__push_range_v4(parser, redis_key)
        elif key == self.inet6num:
            self.ipv4 = False
            self.__push_range_v6(parser, redis_key)
        subkey = ':' + key[1:-1]
        self.push_mntners(parser, redis_key, subkey)
        self.push_persons(parser, redis_key, subkey)
        self.push_diverses_aut_num(parser, redis_key, subkey)
        self.push_origin(parser, redis_key)
        self.push_irt(parser, redis_key)

    def ugly_fix_false_ips(self, subnet):
        # Hack in case the subnet is false in the db...
        splitted_subnet = subnet.split('/')
        i = len(splitted_subnet[0]) - 1 
        while(splitted_subnet[0][i] != ':'):
            i -= 1
        ip = splitted_subnet[0][0:i+1] + '/'
        subnet = ip + splitted_subnet[1]
        try:
            network = IPy.IP(subnet)
        except:
            ip = splitted_subnet[0] + '/'
            i = int(splitted_subnet[1])
            while i <= 128:
                subnet = ip + str(i)
                i += 1
                print subnet
                try:
                    network = IPy.IP(subnet)
                    break
                except:
                    continue
        print network
        return network

    def __push_range_v6(self, parser, net_key):
        subnet = parser.inet6num[0]     
        try:
            network = IPy.IP(subnet)
        except: 
            network = self.ugly_fix_false_ips(subnet)
        first = network.net()
        last = network.broadcast()
        self.push_range(first, last, net_key, self.ipv4)

    def __push_range_v4(self, parser, net_key):
        try:
            first = IPy.IP(parser.inetnum[0][0])
            last = IPy.IP(parser.inetnum[0][1])
        except:
            # The ip is (probably) on the second line....
            first = IPy.IP(parser.inetnum2l[0][0])
            last = IPy.IP(parser.inetnum2l[0][1])
        self.push_range(first, last, net_key, self.ipv4)
    
    # We need a particular push function: some of the 'keys' are not really keys... : 
    # person is a name, and role is... something we want the nic-hdl:person and nic-hdl:role as key into redis
    def push_into_db(self):
        self.redis_whois_server = redis.Redis(db=int(self.config.get('whois_server','redis_db')) )
        for key, entries in self.keys.iteritems():
#            print('Begin' + key)
            while len(entries) > 0 :
                entry = entries.pop()
                if key in self.nic_keys:
                    redis_key = re.findall('nic-hdl:[ ]*(.*)', entry)[0]
                    redis_key += ':' + key[1:-1]
                else:
                    redis_key = re.findall(key + '[ ]*(.*)', entry)[0]
                self.redis_whois_server.set(redis_key, entry)
                self.push_helper_keys(key, redis_key, entry)
        self.pending_keys = 0


if __name__ == "__main__":
    ripe = InitRIPE()
    ripe.start()
