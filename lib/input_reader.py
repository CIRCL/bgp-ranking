
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
config_file = "/home/rvinot/bgp-ranking/etc/bgp-ranking.conf"
config.read(config_file)
root_dir = config.get('directories','root')

# Temporary redis database
temp_reris_db = int(config.get('modules_global','temp_db'))
list_ips = config.get('modules_global','uid_list')
global_db = config.get('redis','global')

# Used if there is a temporaty problem inserting new entries in the DB
sleep_timer = int(config.get('sleep_timers','short'))

class InputReader():
    separator = config.get('input_keys','separator')
    
    key_ip = config.get('input_keys','ip')
    key_src = config.get('input_keys','src')
    key_list_tstamp = config.get('input_keys','list_tstamp')
    key_tstamp = config.get('input_keys','tstamp')
    key_infection = config.get('input_keys','infection')
    key_raw = config.get('input_keys','raw')
    key_times = config.get('input_keys','times')

    def connect(self):
        self.temp_db = redis.Redis(db=temp_reris_db)
        self.temp_db_slave = redis.Redis(port = int(config.get('redis','port_cache')), db=temp_reris_db)
        self.global_db = redis.Redis(db=global_db)

    def get_all_information(self):
        uid = self.temp_db.spop(list_ips)
        if uid is None:
            return None
        ip_key =        '{uid}{sep}{key}'.format(uid = uid , sep = self.separator, key = self.key_ip)
        src_key =       '{uid}{sep}{key}'.format(uid = uid , sep = self.separator, key = self.key_src)
        timestamp_key = '{uid}{sep}{key}'.format(uid = uid , sep = self.separator, key = self.key_tstamp)
        infection_key = '{uid}{sep}{key}'.format(uid = uid , sep = self.separator, key = self.key_infection)
        raw_key =       '{uid}{sep}{key}'.format(uid = uid , sep = self.separator, key = self.key_raw)
        times_key =     '{uid}{sep}{key}'.format(uid = uid , sep = self.separator, key = self.key_times)
        
        table_keys = [ip_key, src_key, timestamp_key, infection_key, raw_key, times_key]
        
        ip, src, timestamp, infection, raw, times = self.temp_db.mget(table_keys)
        if timestamp is None:
            timestamp = datetime.date.today()
        else:
            timestamp = dateutil.parser.parse(timestamp)
        # FIXME pipeline -> every X loop
        self.temp_db.delete(*table_keys)
        return uid, ip, src, timestamp, infection, raw, times

    def insert(self):
        to_return = False
        i = 0 
        while self.temp_db.scard(list_ips) > 0:
            infos = self.get_all_information()
            if infos is None:
                continue
            uid, ip, src, timestamp, infection, raw, times = infos
            if ip is None:
                syslog.syslog(syslog.LOG_ERR, 'Entry without IP, invalid')
                continue
            if src is None:
                syslog.syslog(syslog.LOG_ERR, ip + ' without source, invalid')
                continue
            if timestamp.date() < datetime.date.today() and int(config.get('modules_global','allow_old_entries')) == 0:
                #syslog.syslog(syslog.LOG_ERR, 'The timestamp (' + timestamp.isoformat() + ') of ' + ip + ' is old, entry not imported')
                continue
            try:
                # Check and normalize the IP 
                ip_bin = IPy.IP(ip)
                # FIXME: the second part of the 'if' is due to a "bug" in the version of IPy 
                #           provided by default in debian: 223/8 is not reserved anymore.
                if ip_bin.iptype() != 'PUBLIC' and ip_bin not in IPy.IP('223/8'):
                    syslog.syslog(syslog.LOG_ERR, str(ip_bin) + ' is not a PUBLIC IP Address but is ' + ip_bin.iptype())
                    continue
                ip = ip_bin.strCompressed()
            except:
                syslog.syslog(syslog.LOG_ERR, 'This IP: ' + ip + ' in invalid.')
                continue
            
            iso_timestamp = timestamp.isoformat()
            date = timestamp.date().isoformat()
            index_day_src   = '{date}{sep}{key}'.format(sep = self.separator, date=date, key=config.get('input_keys','index_sources'))
            index_day_ips   = '{temp}{sep}{date}{sep}{source}{sep}{key}'.format(sep = self.separator, date=date, \
                                                                temp = config.get('input_keys','temp'), source=src, \
                                                                key=config.get('input_keys','index_ips'))
            ip_details      = '{ip}{sep}{timestamp}'.format(sep = self.separator, ip = ip, timestamp = iso_timestamp)
            
            to_return = True
            # FIXME pipeline -> every X loop ? 
            pipeline = self.global_db.pipeline()
            pipeline_slave = self.temp_db_slave.pipeline()
            pipeline.sadd(index_day_src, src)
            pipeline_slave.sadd(index_day_ips, ip_details)
            
            ip_details_keys = '{ip_details}{sep}'.format(ip_details = ip_details, sep = self.separator)
            
            if infection is not None:
                pipeline.set('{ip}{key}'.format(ip = ip_details_keys, key = self.key_infection), infection)
            if raw is not None:
                pipeline.set('{ip}{key}'.format(ip = ip_details_keys, key = self.key_raw), raw)
            if times is not None:
                pipeline.set('{ip}{key}'.format(ip = ip_details_keys, key = self.key_times), times)
            self.temp_db.sadd(config.get('redis','key_temp_ris'), ip)
            pipeline.sadd(config.get('redis','no_asn'), index_day_ips)
            if i > = 10000:
                pipeline.execute()
                pipeline_slave.execute()
                i = 0 
            else:
                i += 1 
        return to_return
