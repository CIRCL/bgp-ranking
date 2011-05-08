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
        config_file = "/path/to/bgp-ranking.conf"
        self.config.read(config_file)
        self.separator = self.config.get('input_keys','separator')
        self.global_db  = redis.Redis(port = int(self.config.get('redis','port_master')),\
                                        db = self.config.get('redis','global'))
        self.history_db = redis.Redis(port = int(self.config.get('redis','port_master')),\
                                        db = self.config.get('redis','history'))
        self.history_db_temp = redis.Redis(port = int(self.config.get('redis','port_cache')),\
                                             db = self.config.get('redis','history'))
        if ip_version == 4:
            self.ip_key = self.config.get('input_keys','rankv4')
        elif ip_version == 6:
            self.ip_key = self.config.get('input_keys','rankv6')

        self.impacts = {}
        items = self.config.items('modules_to_parse')
        for item in items:
            self.impacts[item[0]] = float(item[1])
    
    def get_last_ranking(self):
        """
            Get the timestamp of the ranking
        """
        return self.history_db.get(self.config.get('ranking','latest_ranking'))
                            
    def get_default_date(self):
        """
            Set the default date displayed on the website.
        """
        timestamp = self.get_last_ranking()
        if timestamp is not None:
            timestamp = timestamp.split()
            default_date_raw = dateutil.parser.parse(timestamp[0]).date() - datetime.timedelta(days=1)
        else:
            default_date_raw = datetime.date.today() - datetime.timedelta(days=1)
        default_date = default_date_raw.isoformat()
        return default_date_raw, default_date

    def get_sources(self, date):
        """
            Get the sources parsed on a `date`
        """
        return self.global_db.smembers('{date}{sep}{key}'.format(  date   = date, \
                            sep    = self.separator,\
                            key    = self.config.get('input_keys','index_sources')))

    def get_dates(self):
        """
            Get the dates where there is a ranking available in the database
        """
        return self.history_db_temp.smembers(self.config.get('ranking','all_dates'))

    
    def get_daily_rank(self, asn, date, source = None):
        """
            Get the rank of an AS for a particular `source` and `date`
        """
        if source is None:
            source = self.config.get('input_keys','histo_global')
        return self.history_db.get(\
                    '{asn}{sep}{date}{sep}{source}{sep}{ip_key}'.format(sep     = self.separator,\
                                                                        asn     = asn,\
                                                                        date    = date,\
                                                                        source  = source,\
                                                                        ip_key  = self.ip_key))
    