# -*- coding: utf-8 -*-
"""
    bgp_ranking.lib.InputReader
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Insert the new data from the datasets in the database.

"""

import time
import datetime
import dateutil.parser
import redis

import IPy

import syslog

import os
import sys
import ConfigParser

class InputReader(object):
    """
        Filter and sort the new entries given by the modules.
        Ensure that:

        * the entry is valid: has an IP and a source
        * the entry is not already here
    """

    def __init__(self):

        syslog.openlog('BGP_Ranking_Input', syslog.LOG_PID, syslog.LOG_LOCAL5)
        self.config = ConfigParser.RawConfigParser()
        config_file = "/path/to/bgp-ranking.conf"
        self.config.read(config_file)

        # Temporary redis database
        self.list_ips = self.config.get('modules_global','uid_list')

        self.separator = self.config.get('input_keys','separator')

        self.key_ip          = self.config.get('input_keys','ip')
        self.key_src         = self.config.get('input_keys','src')
        self.key_tstamp      = self.config.get('input_keys','tstamp')


    def connect(self):
        """
            Connection to the redis instances
        """
        self.temp_db    = redis.Redis(port = int(self.config.get('redis','port_cache')),\
                            db=int(self.config.get('modules_global','temp_db')))
        self.global_db  = redis.Redis(port = int(self.config.get('redis','port_master')),\
                            db=int(self.config.get('redis','global')))

    def get_all_information(self):
        """
            Extract from the database all the information provided by the modules.
        """
        uid = self.temp_db.spop(self.list_ips)
        if uid is None:
            return None
        ip_key =        '{uid}{sep}{key}'.format(uid = uid , sep = self.separator, key = self.key_ip)
        src_key =       '{uid}{sep}{key}'.format(uid = uid , sep = self.separator, key = self.key_src)
        timestamp_key = '{uid}{sep}{key}'.format(uid = uid , sep = self.separator, key = self.key_tstamp)

        table_keys = [ip_key, src_key, timestamp_key]

        ip, src, timestamp = self.temp_db.hmget(uid, table_keys)
        if timestamp is None:
            timestamp = datetime.date.today()
        else:
            timestamp = dateutil.parser.parse(timestamp)
        self.temp_db.delete(uid)
        return uid, ip, src, timestamp

    def insert(self):
        """
            Re-insert in the database the data provided by the module and
            extracted by :meth:`get_all_information` in a sorted form.
        """
        to_return = False
        while self.temp_db.scard(self.list_ips) > 0:
            infos = self.get_all_information()
            if infos is None:
                continue
            uid, ip, src, timestamp = infos
            if ip is None:
                syslog.syslog(syslog.LOG_ERR, 'Entry without IP, invalid')
                continue
            if src is None:
                syslog.syslog(syslog.LOG_ERR, ip + ' without source, invalid')
                continue
            if timestamp.date() < datetime.date.today() and int(self.config.get('modules_global','allow_old_entries')) == 0:
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
            index_day_src   = '{date}{sep}{key}'.format(sep = self.separator, date=date, key=self.config.get('input_keys','index_sources'))
            index_day_ips   = '{temp}{sep}{date}{sep}{source}{sep}{key}'.format(sep = self.separator, date=date, \
                                                                temp = self.config.get('input_keys','temp'), source=src, \
                                                                key=self.config.get('input_keys','index_ips'))
            ip_details      = '{ip}{sep}{timestamp}'.format(sep = self.separator, ip = ip, timestamp = iso_timestamp)

            to_return = True
            self.global_db.sadd(index_day_src, src)
            pipeline_temp_db = self.temp_db.pipeline()
            pipeline_temp_db.sadd(index_day_ips, ip_details)
            pipeline_temp_db.sadd(self.config.get('redis','key_temp_ris'), ip)
            pipeline_temp_db.sadd(self.config.get('redis','no_asn'), index_day_ips)
            pipeline_temp_db.execute()
        return to_return
