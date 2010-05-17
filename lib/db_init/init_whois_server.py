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


if use_tmpfs:
    tmpfs_size = config.get('whois_server','tmpfs_size')
    if not os.path.ismount(unpack_dir):
        print('Mount the tmpfs directory')
        os.popen('mount -t tmpfs -o size=' + tmpfs_size + ' tmpfs ' + unpack_dir)





archive = archive_arin 
dump = dump_arin

archive = os.path.join(whois_db,archive)
extracted = os.path.join(unpack_dir,dump)
print('Unpack database dump')
#os.popen('gunzip -c ' + archive + ' > ' + extracted)

# temp, for tests... 
#full_db = open(os.path.join(unpack_dir,"ripetest")).read()
splitted = open(extracted).read()

import re

splitted = re.split('\n\n',splitted)
errors = []
  
keys = keys_arin

while len(splitted) > 0:
    entry = splitted.pop()
    if len(entry) > 0 and not re.match('^#', entry):
        ok = False
        for key, entries in keys:
            if re.match(key, entry):
                entries.append(entry)
                ok = True
                break
        if not ok:
            print(entry)
            sys.exit(1)
            errors.append(entry)

import redis 
whois_redis_db = 10 
redis_whois_server = redis.Redis(db=whois_redis_db)

for key,entries in keys:
    print('Begin' + key)
    while len(entries) > 0 :
        entry = entries.pop()
        redis_key = re.findall(key + '[ \t]*(.*)', entry)[0]
        redis_whois_server.set(redis_key.replace(' ', '_'), entry)
    entries = []


if use_tmpfs:
    if os.path.ismount(unpack_dir):
        print('Umount the tmpfs directory')
        os.popen('umount ' + unpack_dir)
else:
#    os.unlink(extracted)
    pass

#import shutil
#shutil.copy(serial,last_parsed_serial)
