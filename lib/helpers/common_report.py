#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Common Report
    ~~~~~~~~~~~~~

    Mother class of all the modules who are using the reports.

"""

import ConfigParser
import redis
import dateutil.parser
import datetime

class CommonReport(object):
    """
        Some values are used quite often. Thanks to this class, the code to get them
        will not be repeated everywhere.
    """

    def __init__(self, ip_version):
        self.config = ConfigParser.RawConfigParser()
        self.config.optionxform = str
        config_file = "/etc/bgpranking/bgpranking.conf"
        self.config.read(config_file)
        self.global_db  = redis.Redis(host=self.config.get('redis','host_master1'),
                port=int(self.config.get('redis','port_master1')),
                db = self.config.get('redis','global'))
        self.history_db = redis.Redis(
                host=self.config.get('redis','host_master2'),
                port = int(self.config.get('redis','port_master2')),
                db = self.config.get('redis','history'))
        self.history_db_temp = redis.Redis(port =
                int(self.config.get('redis','port_cache')),
                db = self.config.get('redis','history'))
        if ip_version == 4:
            self.ip_key = 'rankv4'
        elif ip_version == 6:
            self.ip_key = 'rankv4'

    def get_last_ranking(self):
        """
            Get the timestamp of the ranking
        """
        return self.history_db.get('latest_ranking')

    def get_default_date(self):
        """
            Set the default date displayed on the website.
        """
        timestamp = self.get_last_ranking()
        if timestamp is not None:
            timestamp = timestamp.split()
            default_date_raw = dateutil.parser.\
                    parse(timestamp[0]).date() - datetime.timedelta(days=1)
        else:
            default_date_raw = datetime.date.today() - datetime.timedelta(days=1)
        default_date = default_date_raw.isoformat()
        return default_date_raw, default_date

    def get_dates(self):
        """
            Get the dates where there is a ranking available in the database
        """
        return sorted(self.history_db_temp.smembers('all_dates'))

    def get_sources(self, date):
        """
            Get the sources parsed on a `date`
        """
        return sorted(self.global_db.smembers('{date}|sources'.format(
            date = date)))

    def get_multiple_daily_rank(self, asn_list, date, source):
        """
            Get the rakns of multiple ASNs in one query
        """
        string = '|{date}|{source}|{ip_key}'.format(
                date = date, source = source, ip_key = self.ip_key)
        to_get = ['{asn}{string}'.format(asn = asn, string = string)
                for asn in asn_list]
        if len(to_get) != 0:
            return self.history_db.mget(to_get)
        else :
            return None

    def get_daily_rank_client(self, asn, date, source = None):
        """
            Get a single rank *from the temporary database*
        """
        if source is None:
            source = 'global'
        histo_key = '{date}|{histo_key}|{ip_key}'.format(
                date = date, histo_key = source, ip_key = self.ip_key)
        return self.history_db_temp.zscore(histo_key, asn)
