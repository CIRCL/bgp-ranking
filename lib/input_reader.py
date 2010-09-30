from db_models.ranking import *


import datetime 
import redis

import syslog
syslog.openlog('BGP_Ranking_Input', syslog.LOG_PID, syslog.LOG_USER)

# Temporary redis database
temp_reris_db = int(config.get('modules_global','temp_db'))
list_ips = config.get('modules_global','uid_list')

class InputReader():
    key_ip = ':ip'
    key_src = ':source'
    key_tstamp = ':timestamp'
    key_infection = ':infection'
    key_raw = ':raw'
    key_times = ':times'
    
    def __init__(self):
        self.temp_db = redis.Redis(db=temp_reris_db)
    
    def insert(self):
        to_return = False
        while self.temp_db.scard(list_ips) > 0:
            to_return = True
            uid = str(self.temp_db.spop(list_ips))
            keys = self.temp_db.keys(uid + ':*')
            if len(keys) == 0:
                continue
            ip = self.temp_db.get(uid + self.key_ip)
            src = self.temp_db.get(uid + self.key_src)
            timestamp = self.temp_db.get(uid + self.key_tstamp)
            infection = self.temp_db.get(uid + self.key_infection)
            raw = self.temp_db.get(uid + self.key_raw)
            times = self.temp_db.get(uid + self.key_times)
            # NOTE: very elegant way to drop a list of keys :)
            self.temp_db.delete(*keys)
            try:
                # Check and normalize the IP 
                ip_temp = IPy.IP(ip)
                if ip_temp.iptype() != 'PUBLIC':
                    syslog.syslog(syslog.LOG_ERR, str(ip_temp) + ' is not a PUBLIC IP Address but is ' + ip_temp.iptype())
                    continue
                ip = str(ip_temp)
            except:
                syslog.syslog(syslog.LOG_ERR, 'error with IP:' + ip)
                continue
            if src is None:
                syslog.syslog(syslog.LOG_ERR, ip + ' without source, invalid')
                continue
            if timestamp is None:
                timestamp = datetime.date.today()
            if times is None:
                times = 1
            #IP = IPs.query.get(unicode(ip))
            #if IP is None:
                #IP = IPs(ip=unicode(ip))
            #if IPsDescriptions.query.filter_by(ip=IP, list_name=unicode(self.name),\
                                                #list_date=current_timestamp).first() is None:
                #IPsDescriptions(ip=IP, list_name=unicode(src), list_date=timestamp, \
                                #infection=unicode(infection), raw_informations=unicode(raw), times=times)
            #else:
                #syslog.syslog(syslog.LOG_ERR, ip + ' already there.')
        return to_return