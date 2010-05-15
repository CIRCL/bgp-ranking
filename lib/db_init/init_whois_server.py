#!/usr/bin/python
# -*- coding: utf-8 -*-

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
errors = []

keys_ripe =  [
  ['^aut-num:'   , aut_num_entries],
  ['^route:'     , route_entries],
  ['^route6:'    , route6_entries],
  ['^as-block:'  , as_block_entries],
  ['^as-set:'    , as_set_entries],
  ['^domain:'    , domain_entries],
  ['^rtr-set:'   , rtr_set_entries],
  ['^route-set:' , route_set_entries],
  ['^inet6num:'  , inet6num_entries],
  ['^inetnum:'   , inetnum_entries],
  ['^org:'       , org_entries],
  ['^poetic-form:', poetic_form_entries],
  ['^poem:'      , poem_entries],
  ['^peering-set:', peering_set_entries],
  ['^limerick:'  , limerick_entries],
  ['^key-cert:'  , key_cert_entries],
  ['^inet-rtr:'  ,  inet_rtr_entries],
  ['^filter_set' , filter_set_entries]]


while len(splitted) > 0:
    entry = splitted.pop()
    if len(entry) > 0 and not re.match('^#', entry):
		ok = False
        for key, entries in keys_ripe:
            if re.match(key, entry):
                entries.append(entry)
				ok = true
                break
		if not ok: 
			errors.append(entry)

print (errors)
sys.exit(1)
import redis 
whois_redis_db = 10 
redis_whois_server = redis.Redis(db=whois_redis_db)

for key,entries in key_ripe:
	for entry in entries:
		redis_key = re.findall(key + '[ \t]*(.*)', entry)[0]
		redis_whois_server.set(redis_key.replace(' ', '_'), entry)
	entries = None


if use_tmpfs:
    if os.path.ismount(unpack_dir):
        print('Umount the tmpfs directory')
        os.popen('umount ' + unpack_dir)
else:
#    os.unlink(extracted)
    pass

#import shutil
#shutil.copy(serial,last_parsed_serial)
