#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Reports
    ~~~~~~~
    
    Generate reports for a particular day.
"""
import os 
import sys
import ConfigParser

import datetime
import redis
from IPy import IP
import dateutil.parser

from helpers.common_report import CommonReport

class Reports(CommonReport):
    """
        This class is used to generate reports for a day 
        (you can also choose between IPv4 and IPv6)
    """

    def __init__(self, ip_version = 4):
        CommonReport.__init__(self, ip_version)
        self.config_db = redis.Redis(port = int(self.config.get('redis','port_master')),\
                                       db = self.config.get('redis','config'))
        self.set_default_date()
        self.set_sources()
    
    def set_default_date(self):
        """
            Set the default date displayed on the website.
        """
        self.default_date_raw, self.default_date = self.get_default_date()

    def set_sources(self, date = None):
        """
            Set the sources parsed on a `date`
        """
        self.sources = self.get_sources(date)

    def get_sources(self, date = None):
        """
            Get the sources parsed on a `date`
        """
        if date is None:
            date = self.default_date
        return super(Reports, self).get_sources(date)

    def get_daily_rank(self, asn, source = None, date = None):
        """
            Get the rank of an AS for a particular `source` and `date`
        """
        if date is None:
            date = self.default_date
        return super(Reports, self).get_daily_rank(asn, date, source)
    
    def flush_temp_db(self):
        """
            Drop the whole temporary ranking database.
        """
        self.history_db_temp.flushdb()


    def build_reports_lasts_days(self, nr_days = 2):
        """
            Build the reports of the `nr_days` last days 
        """
        if nr_days <= 0:
            return
        nr_days += 1
        for i in range(1, nr_days):
            date = self.default_date_raw - datetime.timedelta(i)
            iso_date = date.isoformat()
            self.build_reports(iso_date)

    def build_last_reports(self):
        self.build_reports()
        timestamp = self.get_last_ranking()
        if timestamp is not None:
            timestamp = timestamp.split()
            to_build = dateutil.parser.parse(timestamp[0]).date()
            self.build_reports(to_build.isoformat())
    
    def build_reports(self, date = None):
        """
            Build all the reports: for all the sources independently and the global one
        """
        if date is None:
            date = self.default_date
        set_days = self.config.get('ranking','all_dates')
        self.history_db_temp.sadd(set_days, date)
        self.set_sources(date)
        self.global_report(date)
        for source in self.sources:
            self.source_report(source = source, date = date)
    
    def global_report(self, date = None):
        """
            Build the global report (add all the results of all the sources)
        """
        if date is None:
            date = self.default_date
        # delete the old key
        zset_key = self.config.get('input_keys','histo_global')
        histo_key = '{date}{sep}{histo_key}{sep}{ip_key}'.format(   sep         = self.separator,\
                                                                    date        = date,\
                                                                    histo_key   = zset_key,\
                                                                    ip_key      = self.ip_key)
        self.history_db_temp.delete(histo_key)
        for source in self.sources:
            self.source_report(source, zset_key, date)

    def build_asns_by_source(self, source, date = None):
        """
            Create a bunch of keys to easily find the sources associed to the asn/subnet
        """
        if source == self.config.get('input_keys','histo_global'):
            return
        if date is None:
            date = self.default_date
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

    def source_report(self, source, zset_key = None, date = None):
        """
            Build the report of a particular source
        """
        if zset_key is None:
            zset_key = source
        if date is None:
            date = self.default_date
        self.build_asns_by_source(source, date)
        histo_key = '{date}{sep}{histo_key}{sep}{ip_key}'.format(   sep         = self.separator,\
                                                                    date        = date,\
                                                                    histo_key   = zset_key,\
                                                                    ip_key      = self.ip_key)
        if zset_key == source:
            # delete the old key if we are not in the "global" ranking
            self.history_db_temp.delete(histo_key)

        asns = self.global_db.smembers(\
                    '{date}{sep}{source}{sep}{key}'.format( sep     = self.separator,\
                                                            date    = date,\
                                                            source  = source,\
                                                            key     = self.config.get('input_keys','index_asns')))

        pipeline = self.history_db_temp.pipeline(transaction=False)
        for asn in asns:
            if asn != self.config.get('modules_global','default_asn'):
                rank = self.get_daily_rank(asn, source, date)
                if rank is not None:
                    pipeline.zincrby(histo_key, asn, float(rank) * int(self.config_db.get(str(source))))
        pipeline.execute()

    def format_report(self, source = None, limit = 50, date = None):
        """
            Format the report to be displayed in the website
        """
        if source is None:
            source = self.config.get('input_keys','histo_global')
        if date is None:
            date = self.default_date
        histo_key = '{date}{sep}{histo_key}{sep}{ip_key}'.format(   sep         = self.separator,\
                                                                    date        = date,\
                                                                    histo_key   = source,\
                                                                    ip_key      = self.ip_key)

        reports_temp = self.history_db_temp.zrevrange(histo_key, 0, limit, True)
        if reports_temp is None:
            return None
        pipeline = self.history_db_temp.pipeline()
        for report_temp in reports_temp:
            pipeline.smembers('{date}{sep}{asn}'.format(sep     = self.separator,\
                                                        date    = date,\
                                                        asn     = report_temp[0]))
        sources = pipeline.execute()
        report = [list(x) + [', '.join(y)] for x,y in zip(reports_temp,sources)]
        return report

    def prepare_graphe_js(self, asn, first_date, last_date, sources = None):
        """
            Prepare the JavaScript graph of an AS between `first_date` and `last_date` for a `source`
        """
        dates = []
        current = first_date
        while current <= last_date:
            dates.append(current.strftime("%Y-%m-%d"))
            current += datetime.timedelta(days=1)

        pipeline = self.global_db.pipeline()
        for date in dates:
            pipeline.smembers(\
                '{date}{sep}{key}'.format(  date    = date,\
                                            sep     = self.separator,\
                                            key     = self.config.get('input_keys','index_sources')))

        lists_sources = pipeline.execute()
        all_sources = set(()).union(*lists_sources)

        if sources is None:
            sources = all_sources
        else:
            sources = [sources]

        keys = {}
        ranks = {}
        pipeline = self.history_db.pipeline()
        for source in sources:
            keys[source] = []
            for date in dates:
                keys[source].append(\
                    '{asn}{sep}{date}{sep}{source}{sep}{v4}'.format(sep     = self.separator,\
                                                                    asn     = asn,\
                                                                    date    = date,\
                                                                    source  = source,\
                                                                    v4      = self.config.get('input_keys','rankv4')))

            pipeline.mget(keys[source])
        histories = pipeline.execute()
        if len(histories) == 0:
            # Nothing to display, quit
            return {}
        i = 0 
        for source in sources:
            ranks[source] = histories[i]
            i += 1 

        ranks_by_days = {}
        for source in sources:
            i = 0 
            for rank in ranks[source]:
                if rank is not None:
                    asn_day = dates[i]
                    if ranks_by_days.get(asn_day, None) is None:
                        ranks_by_days[asn_day] = float(rank) *  int(self.config_db.get(str(source)))]
                    else:
                        ranks_by_days[asn_day] += float(rank) *  int(self.config_db.get(str(source)))]
                i += 1 
        for ranks in ranks_by_days:
            ranks_by_days[ranks] += 1 
        return ranks_by_days
        
    def get_asn_descs(self, asn, sources = None, date = None):
        """
            Get the details of an ASN
        """
        if sources is None:
            sources = self.sources
        else:
            sources = [sources]
        if date is None:
            date = self.default_date
        timestamps = self.global_db.smembers(asn)
        if len(timestamps) == 0:
            # The ASN does not exists in the database
            return [], []
        current_asn_sources = self.history_db_temp.smembers(\
                                    '{date}{sep}{asn}'.format(  date    = date,\
                                                                sep     = self.separator,\
                                                                asn     = asn))
        asn_descs_to_print = []
        for timestamp in timestamps:
            asn_timestamp_temp = '{date}{sep}{asn}{sep}{timestamp}'.format( sep         = self.separator,\
                                                                            date        = date,\
                                                                            asn         = asn,\
                                                                            timestamp   = timestamp)
            asn_timestamp_key = '{asn}{sep}{timestamp}{sep}'.format(sep = self.separator, asn = asn, timestamp = timestamp)
            nb_of_ips = 0 
            pipeline = self.global_db.pipeline()
            for source in sources:
                pipeline.scard('{asn_timestamp_key}{date}{sep}{source}'.format(sep = self.separator, \
                                    asn_timestamp_key = asn_timestamp_key, date = date, source=source))
            ips_by_sources = pipeline.execute()
            nb_of_ips += sum(ips_by_sources)
            if nb_of_ips > 0:
                keys = ['{asn_timestamp_key}{owner}'.   format(asn_timestamp_key = asn_timestamp_key, \
                                                                           owner = self.config.get('input_keys','owner')),
                        '{asn_timestamp_key}{ip_block}'.format(asn_timestamp_key = asn_timestamp_key, \
                                                                        ip_block = self.config.get('input_keys','ips_block'))]
                owner, ip_block = self.global_db.mget(keys)
                local_rank = 0.0
                i = 0 
                for source in sources:
                    local_rank += float(ips_by_sources[i]) *  int(self.config_db.get(str(source)))]
                    i += 1
                sources_web = self.history_db_temp.smembers(asn_timestamp_temp)
                asn_descs_to_print.append([asn, timestamp, owner, ip_block,\
                                            nb_of_ips, ', '.join(sources_web), 1 + local_rank / IP(ip_block).len()])
        to_return = sorted(asn_descs_to_print, key=lambda desc: desc[6], reverse = True)
        return to_return, current_asn_sources


    def get_ips_descs(self, asn, asn_timestamp, sources = None, date = None):
        """
            Get the details of an IP
        """
        if sources is None:
            sources = self.sources
        else:
            sources = [sources]
        if date is None:
            date = self.default_date
        key_list_tstamp = self.config.get('input_keys','list_tstamp')
        key_infection = self.config.get('input_keys','infection')
        key_raw = self.config.get('input_keys','raw')
        key_whois = self.config.get('input_keys','whois')

        
        asn_timestamp_key = '{asn}{sep}{timestamp}{sep}'.format(asn = asn, sep = self.separator, timestamp = asn_timestamp)
        pipeline = self.global_db.pipeline()
        for source in sources:
            pipeline.smembers('{asn_timestamp_key}{date}{sep}{source}'.format(sep = self.separator, \
                                        asn_timestamp_key = asn_timestamp_key, date = date, source=source))
        ips_by_source = pipeline.execute()
        if len(ips_by_source) == 0:
            return []
        ip_descs_to_print = []
        i = 0
        for source in sources:
            ips = ips_by_source[i]
            for ip_details in ips:
                ip, timestamp = ip_details.split(self.separator)
                ip_descs_to_print.append([timestamp, ip, source])
            i += 1
        to_return = sorted(ip_descs_to_print, key=lambda desc: IP(desc[1]).int())
        return to_return
