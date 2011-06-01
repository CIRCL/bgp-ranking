#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Reports Generator
    ~~~~~~~~~~~~~~~~~
    
    Generate reports for a particular day.
"""

from helpers.common_report import CommonReport
import redis
import datetime

class ReportsGenerator(CommonReport):

    def __init__(self, ip_version = 4):
        CommonReport.__init__(self, ip_version)
        self.config_db = redis.Redis(port = int(self.config.get('redis','port_master')),\
                                       db = self.config.get('redis','config'))

    def flush_temp_db(self):
        """
            Drop the whole temporary ranking database.
        """
        self.history_db_temp.flushdb()

    def build_reports_lasts_days(self, nr_days = 2):
        """
            Build the reports of the `nr_days` last days, begins with "default date"
        """
        if nr_days <= 0:
            return
        nr_days += 1
        default_date_raw = self.get_default_date()[0]
        for i in range(1, nr_days):
            self.build_reports(default_date_raw.isoformat())
            default_date_raw = default_date_raw - datetime.timedelta(i)

    def build_last_reports(self):
        """
            Build last available report (today if there is something to report)
        """
        self.build_reports(datetime.date.today().isoformat())

    def build_reports(self, date):
        """
            Build all the reports: for all the sources independently and the global one
        """
        sources = self.get_sources(date)
        if len(sources) == 0:
            return
        self.history_db_temp.sadd(self.config.get('ranking','all_dates'), date)
        for source in sources:
            self.source_report(source = source, date = date)
        self.global_report(date)

    def source_report(self, source, date):
        """
            Build the report of a particular source
        """
        self.build_asns_by_source(source, date)
        histo_key = '{date}{sep}{histo_key}{sep}{ip_key}'.format(   sep         = self.separator,\
                                                                    date        = date,\
                                                                    histo_key   = source,\
                                                                    ip_key      = self.ip_key)
        # delete the old key
        self.history_db_temp.delete(histo_key)

        asns = self.global_db.smembers(\
                    '{date}{sep}{source}{sep}{key}'.format( sep     = self.separator,\
                                                            date    = date,\
                                                            source  = source,\
                                                            key     = self.config.get('input_keys','index_asns')))

        ranks = self.get_multiple_daily_rank(asns, date, source)
        pipeline = self.history_db_temp.pipeline(transaction=False)
        i = 0
        for asn in asns:
            if asn != self.config.get('modules_global','default_asn'):
                rank = ranks[i]
                if rank is not None:
                    pipeline.zadd(histo_key, asn, float(rank) * float(self.config_db.get(str(source))))
            i += 1
        pipeline.execute()

    def build_asns_by_source(self, source, date):
        """
            Create a bunch of keys to easily find the sources associed to the asn/subnet
        """
        asns_details = self.global_db.smembers(\
                            '{date}{sep}{source}{sep}{key}'.format( sep     = self.separator,\
                                                                    date    = date,\
                                                                    source  = source,\
                                                                    key     = self.config.get('input_keys','index_asns_details')))
        pipeline = self.history_db_temp.pipeline(transaction=False)
        for detail in asns_details:
            asn, ts = detail.split(self.separator)
            pipeline.sadd('{date}{sep}{asn}'.format(date = date, sep = self.separator, asn = asn), source)
            pipeline.sadd('{date}{sep}{detail}'.format(date = date, sep = self.separator, detail = detail), source)
        pipeline.execute()

    def global_report(self, date):
        """
            Build the global report (add all the results of all the sources)
        """
        histo_key = '{date}{sep}{histo_key}{sep}{ip_key}'.format(\
                            sep         = self.separator,\
                            date        = date,\
                            histo_key   = self.config.get('input_keys','histo_global'),\
                            ip_key      = self.ip_key)

        string = '{date}{sep}{source}{sep}{ip_key}'
        # generate list of zsets to merge
        to_merge = [ string.format( sep     = self.separator, date  = date,\
                                    source  = source,         ip_key= self.ip_key)
                            for source in self.get_sources(date) ]
        self.history_db_temp.zunionstore(histo_key, to_merge)
