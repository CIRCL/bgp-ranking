
import time
import datetime 
import dateutil.parser
import redis

import IPy

import syslog
syslog.openlog('BGP_Ranking_Input', syslog.LOG_PID, syslog.LOG_USER)

import os 
import sys
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read("../bgp-ranking.conf")
root_dir = config.get('directories','root')

# Temporary redis database
temp_reris_db = int(config.get('modules_global','temp_db'))
list_ips = config.get('modules_global','uid_list')
global_db = config.get('redis','global_db')

# Used if there is a temporaty problem inserting new entries in the DB
sleep_timer = int(config.get('sleep_timers','short'))

class InputReader():
    key_ip = config.get('input_keys','ip')
    key_src = config.get('input_keys','src')
    key_tstamp = config.get('input_keys','tstamp')
    key_infection = config.get('input_keys','infection')
    key_raw = config.get('input_keys','raw')
    key_times = config.get('input_keys','times')
    
    key_no_asn = config.get('input_keys','no_asn')

    def connect(self):
        self.temp_db = redis.Redis(db=temp_reris_db)
        self.global_db = redis.Redis(db=global_db)

    def get_all_information(self):
        uid = str(self.temp_db.spop(list_ips))
        ip = self.temp_db.get(uid + self.key_ip)
        src = self.temp_db.get(uid + self.key_src)
        timestamp = self.temp_db.get(uid + self.key_tstamp)
        if timestamp is None:
            timestamp = datetime.datetime.utcnow()
        else:
            timestamp = dateutil.parser.parse(timestamp)
        infection = self.temp_db.get(uid + self.key_infection)
        raw = self.temp_db.get(uid + self.key_raw)
        times = self.temp_db.get(uid + self.key_times)
        self.temp_db.delete(uid + self.key_ip, uid + self.key_src, uid + self.key_tstamp, uid + self.key_infection, uid + self.key_raw, uid + self.key_times)
        return uid, ip, src, timestamp, infection, raw, times

    def insert(self):
        to_return = False
        while self.temp_db.scard(list_ips) > 0:
            to_return = True
            uid, ip, src, timestamp, infection, raw, times = self.get_all_information()
            if ip is None:
                syslog.syslog(syslog.LOG_ERR, 'Entry without IP, invalid')
                continue
            if src is None:
                syslog.syslog(syslog.LOG_ERR, ip + ' without source, invalid')
                continue
            try:
                # Check and normalize the IP 
                ip_temp = IPy.IP(ip)
                # FIXME: the second part of the 'if' is due to a "bug" in the version of IPy 
                #           provided by default in debian: 223/8 is not reserved anymore.
                if ip_temp.iptype() != 'PUBLIC' and ip_temp not in IPy.IP('223/8'):
                    syslog.syslog(syslog.LOG_ERR, str(ip_temp) + ' is not a PUBLIC IP Address but is ' + ip_temp.iptype())
                    continue
                ip = str(ip_temp)
            except:
                syslog.syslog(syslog.LOG_ERR, 'This IP: ' + ip + ' in invalid.')
                continue
            
            unique_timestamp = datetime.datetime.utcnow().isoformat()
            index_ips = '{date}:{source}'.format(date=timestamp.date().isoformat(), source=src)
            ip_information = '{ip}:{index}'.format(ip=ip, index=index_ips)
            ip_details = '{infos}:{timestamp}'.format(infos=ip_information, timestamp=unique_timestamp)
            
            self.global_db.sadd(ip_information, unique_timestamp)
            self.global_db.sadd(index_ips, ip)
            self.global_db.sadd(self.key_no_asn, ip_details)
            
            if infection is not None:
                self.global_db.set(ip_details + key_infection, infection)
            if raw is not None:
                self.global_db.set(ip_details + key_raw, raw)
            if times is not None:
                self.global_db.set(ip_details + key_times, times)
            
            self.temp_db.sadd(config.get('redis','key_temp_ris'), ip)
        return to_return
