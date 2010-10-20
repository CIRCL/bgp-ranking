from db_models.ranking import *


import datetime 
import dateutil.parser
import redis

import IPy

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

    def connect(self):
        self.temp_db = redis.Redis(db=temp_reris_db)

    def mysql_error(self, uid, ip, src, timestamp, infection, raw, times):
        self.temp_db.set(uid + self.key_ip, ip)
        self.temp_db.set(uid + self.key_src, src)
        self.temp_db.set(uid + self.key_tstamp, str(timestamp))
        self.temp_db.set(uid + self.key_infection, infection)
        self.temp_db.set(uid + self.key_raw, raw)
        self.temp_db.set(uid + self.key_times, times)
        self.temp_db.sadd(list_ips, uid)

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
        if times is None:
            times = 1
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
                # FIXME: the second part of the is is dur to a bug in IPy: 223/8 is not reserved anymore.
                if ip_temp.iptype() != 'PUBLIC' and ip_temp not in IPy.IP('223/8'):
                    syslog.syslog(syslog.LOG_ERR, str(ip_temp) + ' is not a PUBLIC IP Address but is ' + ip_temp.iptype())
                    continue
                ip = str(ip_temp)
            except:
                syslog.syslog(syslog.LOG_ERR, 'This IP: ' + ip + ' in invalid.')
                continue
            try:
                # Sometimes, the insertion failed because two process attempt to insert the same new IP in the database at the sametime. 
                # In this case, we will push again later the entry that failed.
                IP = IPs.query.get(unicode(ip))
                if IP is None:
                    IP = IPs(ip=unicode(ip))
                if IPsDescriptions.query.filter_by(ip=IP, list_name=unicode(src),\
                                                    list_date=timestamp).first() is None:
                    IPsDescriptions(ip=IP, list_name=unicode(src), list_date=timestamp, \
                                    infection=unicode(infection), raw_informations=unicode(raw), times=times)
                #else:
                    #syslog.syslog(syslog.LOG_ERR, ip + ' already there.')
            except:
                syslog.syslog(syslog.LOG_ERR, 'Impossible to insert the IP ' + ip + ', try again later.')
                self.mysql_error(uid, ip, src, timestamp, infection, raw, times)
                
        self.r_session = RankingSession()
        self.r_session.commit()
        self.r_session.close()
        return to_return

    def disconnect(self):
        self.temp_db = None
