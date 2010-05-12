#!/usr/bin/python

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../../etc/bgp-ranking.conf")
root_dir = config.get('global','root')
whois_db = os.path.join(root_dir,config.get('global','whois_db'))
unpack_dir = os.path.join(root_dir,config.get('whois_server','unpack_dir'))
use_tmpfs = int(config.get('whois_server','use_tmpfs'))

import tarfile
import filecmp

serial = os.path.join(whois_db,"RIPE.CURRENTSERIAL")
last_parsed_serial = os.path.join(whois_db,"RIPE.CURRENTSERIAL_last")
##if os.path.exists(last_parsed_serial) and filecmp.cmp(serial, last_parsed_serial):
##    print('no new files to parse')
##    exit(1)

if use_tmpfs:
    tmpfs_size = config.get('whois_server','tmpfs_size')
    if not os.path.ismount(unpack_dir):
        print('Mount the tmpfs directory')
        os.popen('mount -t tmpfs -o size=' + tmpfs_size + ' tmpfs ' + unpack_dir)

archive = os.path.join(whois_db,"ripe.db.gz")
extracted = os.path.join(unpack_dir,"ripe.db")
print('Unpack database dump')
#os.popen('gunzip -c ' + archive + ' > ' + extracted)

# temp, for tests... 
#full_db = open(os.path.join(unpack_dir,"ripetest")).read()
full_db = open(extracted).read()

# will be used
#RIPE_keys = {
#    'as-block': re.compile('^as-block:'), 
#    'aut-num':  re.compile('^aut-num:')
#}

import re

splitted = re.split('\n\n',full_db)
full_db = None
aut_num_entries = []
routes6_entries = []
routes_entries = []
as_block_entries = []
as_set_entries = []
domain_entries = []
rtr_set_entries = []
route_set_entries = []
inet6num_entries = []
inetnum_entries = []
org_entries = []
poetic_form_entries = []
poem_entries = []
peering_set_entries = []
limerick_entries = []
key_cert_entries = []
inet_rtr_entries = []
filter_set_entries = [] 

while len(splitted) > 0:
    entry = splitted.pop()
    if len(entry) > 0 and not re.match('^#', entry):
        if re.match('^aut-num:', entry):
            aut_num_entries.append(entry)
        elif re.match('^route:', entry):
            routes6_entries.append(entry)
        elif re.match('^route6:', entry):
            routes_entries.append(entry)
        elif re.match('^as-block:', entry):
            as_block_entries.append(entry)
        elif re.match('^as-set:', entry):
            as_set_entries.append(entry)
        elif re.match('^domain:', entry):
            domain_entries.append(entry)
        elif re.match('^rtr-set:', entry):
            rtr_set_entries.append(entry)
        elif re.match('^route-set:', entry):
            route_set_entries.append(entry)
        elif re.match('^inet6num:', entry):
            inet6num_entries.append(entry)
        elif re.match('^inetnum:', entry):
            inetnum_entries.append(entry)
        elif re.match('^org:', entry):
            org_entries.append(entry)
        elif re.match('^poetic-form:', entry):
            poetic_form_entries.append(entry)
        elif re.match('^poem:', entry):
            poem_entries.append(entry)
        elif re.match('^peering-set:', entry):
            peering_set_entries.append(entry)
        elif re.match('^limerick:', entry):
            limerick_entries.append(entry)
        elif re.match('^key-cert:', entry):
            key_cert_entries.append(entry)
        elif re.match('^inet-rtr:', entry):
            inet_rtr_entries.append(entry)
        elif re.match('^filter-set:', entry):
            filter_set_entries.append(entry)
        else:
            print(entry)
            sys.exit(1)

sys.exit(1)
import redis 

redis_whois_server = redis.Redis(db=10)

for entry in filter_set_entries:
    filter_set = re.findall('inet-rtr:[ \t]*(.*)', entry)[0]
    redis_whois_server.set(filter_set, entry)
filter_set_entries = None

for entry in inet_rtr_entries:
    inet_rtr = re.findall('inet-rtr:[ \t]*(.*)', entry)[0]
    redis_whois_server.set(inet_rtr, entry)
inet_rtr_entries = None

for entry in key_cert_entries:
    key_cert = re.findall('key-cert:[ \t]*(.*)', entry)[0]
    redis_whois_server.set(key_cert, entry)
key_cert_entries = None

for entry in peering_set_entries:
    peering_set = re.findall('peering-set:[ \t]*(.*)', entry)[0]
    redis_whois_server.set(peering_set, entry)
peering_set_entries = None

for entry in limerick_entries:
    limerick = re.findall('limerick:[ \t]*(.*)', entry)[0]
    redis_whois_server.set(limerick, entry)
limerick_entries = None


for entry in inetnum_entries:
    route_set = re.findall('inetnum:[ \t]*(.*)', entry)[0]
    redis_whois_server.set(route_set.replace(' ', '_'), entry)
inetnum_entries = None

for entry in poem_entries:
    poem = re.findall('poem:[ \t]*(.*)', entry)[0]
    redis_whois_server.set(poem, entry)
poem_entries = None

for entry in poetic_form_entries:
    poetic_form = re.findall('poetic-form:[ \t]*(.*)', entry)[0]
    redis_whois_server.set(poetic_form, entry)
poetic_form_entries = None

for entry in org_entries:
    org = re.findall('org:[ \t]*(.*)', entry)[0]
    redis_whois_server.set(org, entry)
org_entries = None


for entry in aut_num_entries:
    asn = re.findall('aut-num:[ \t]*(.*)', entry)[0]
    redis_whois_server.set(asn, entry)
aut_num_entries = None
    
for entry in routes6_entries:
    route = re.findall('route[6]?:[ \t]*(.*)', entry)[0]
    redis_whois_server.set(route, entry)
routes6_entries = None

for entry in routes_entries:
    route = re.findall('route[6]?:[ \t]*(.*)', entry)[0]
    redis_whois_server.set(route, entry)
routes_entries = None
    
for entry in as_block_entries:
    as_block = re.findall('as-block:[ \t]*(.*)', entry)[0]
    redis_whois_server.set(as_block.replace(' ', '_'), entry)
as_block_entries = None

for entry in as_set_entries:
    as_set = re.findall('as-set:[ \t]*(.*)', entry)[0]
    redis_whois_server.set(as_set, entry)
as_set_entries = None

for entry in domain_entries:
    domain = re.findall('domain:[ \t]*(.*)', entry)[0]
    redis_whois_server.set(domain, entry)
domain_entries = None

for entry in rtr_set_entries:
    rtr_set = re.findall('rtr-set:[ \t]*(.*)', entry)[0]
    redis_whois_server.set(rtr_set, entry)
rtr_set_entries = None

for entry in route_set_entries:
    route_set = re.findall('route-set:[ \t]*(.*)', entry)[0]
    redis_whois_server.set(route_set, entry)
route_set_entries = None

for entry in inet6num_entries:
    route6_set = re.findall('inet6num:[ \t]*(.*)', entry)[0]
    redis_whois_server.set(route6_set, entry)
inet6num_entries = None


if use_tmpfs:
    if os.path.ismount(unpack_dir):
        print('Umount the tmpfs directory')
        os.popen('umount ' + unpack_dir)
else:
#    os.unlink(extracted)
    pass

#import shutil
#shutil.copy(serial,last_parsed_serial)
