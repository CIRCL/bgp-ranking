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

class Reports():
    """
        This class is used to generate reports for a day 
        (you can also choose between IPv4 and IPv6)
    """
    
    def get_last_ranking(self):
        """
            Get the timestamp of the ranking
        """
        return redis.Redis(port = int(self.config.get('redis','port_master')),\
                            db   = self.config.get('redis','history')).get(self.config.get('ranking','latest_ranking'))

    def build_reports_lasts_days(self, nr_days = 1):
        if nr_days <= 0:
            return
        set_days = self.config.get('ranking','latest_ranking')
        self.history_db_temp.sadd(set_days, self.date)
        for i in range(nr_days):
            date = self.date_raw - datetime.timedelta(i)
            iso_date = date.isoformat()
            self.build_reports(iso_date)
            self.history_db_temp.sadd(set_days, iso_date)
    
    def display_graphs_prec_day(self, date):
        """
            Unless the ranking of `date` exists, there is nothing to display. 
            
            That is why we will display the ranking of the precedent day
        """
        hours = sorted(self.config.get('routing','update_hours').split())
        first_hour = hours[0]
        timestamp = self.get_last_ranking()
        if timestamp is not None:
            timestamp = timestamp.split()
            if int(timestamp[1]) == int(first_hour) or timestamp[0] != date.strftime("%Y%m%d"):
                return True
        return False
    
    def set_date(self, date):
        """
            Allow to reload the report displayed on the website.
        """
        if self.last_ranking is None or self.last_ranking != self.get_last_ranking():
            self.last_ranking = self.get_last_ranking()

            if self.display_graphs_prec_day(date):
                date = date - datetime.timedelta(1)
            self.date = date.isoformat()

    def set_sources(self, date):
        self.sources =  self.global_db.smembers(\
                            '{date}{sep}{key}'.format(  date   = date, \
                                                        sep    = self.separator,\
                                                        key    = self.config.get('input_keys','index_sources')))
    
    def __init__(self, date, ip_version = 4):
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
        self.last_ranking = None
        self.date_raw = date
        self.set_date(date)
        self.set_sources(self.date)
    
    def build_reports(self, date = None):
        """
            Build all the reports: for all the sources independently and the global one
        """
        if date is None:
            date = self.date
        self.history_db_temp.flushdb()
        self.global_report(date)
        for source in self.sources:
            self.source_report(source = source, date = date)
        # FIXME: only for testing: not necessary to rebuild all the rankings each time
        self.build_reports_lasts_days()
    
    def global_report(self, date = None):
        """
            Build the global report (add all the results of all the sources)
        """
        if date is None:
            date = self.date
        for source in self.sources:
            self.source_report(source, self.config.get('input_keys','histo_global'), date)

    def build_asns_by_source(self, source, date = None):
        """
            Create a bunch of keys to easily find the sources associed to the asn/subnet
        """
        if source == self.config.get('input_keys','histo_global'):
            return
        if date is None:
            date = self.date
        pipeline = self.history_db_temp.pipeline(transaction=False)
        asns_details = self.global_db.smembers(\
                            '{date}{sep}{source}{sep}{key}'.format( sep     = self.separator,\
                                                                    date    = date,\
                                                                    source  = source,\
                                                                    key     = self.config.get('input_keys','index_asns_details')))
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
            date = self.date
        self.build_asns_by_source(source, date)
        histo_key = '{date}{histo_key}{sep}{ip_key}'.format(sep         = self.separator,\
                                                            date        = date,\
                                                            histo_key   = zset_key,\
                                                            ip_key      = self.ip_key)

        asns = self.global_db.smembers(\
                    '{date}{sep}{source}{sep}{key}'.format( sep     = self.separator,\
                                                            date    = date,\
                                                            source  = source,\
                                                            key     = self.config.get('input_keys','index_asns')))

        pipeline = self.history_db_temp.pipeline(transaction=False)
        for asn in asns:
            if asn != self.config.get('modules_global','default_asn'):
                rank = self.get_daily_rank(asn, source)
                if rank is not None:
                    pipeline.zincrby(histo_key, asn, float(rank) * self.impacts[str(source)])
        pipeline.execute()

    def format_report(self, source = None, limit = 50, date = None):
        """
            Format the report to be displayed in the website
        """
        if source is None:
            source = self.config.get('input_keys','histo_global')
        if date is None:
            date = self.date
        histo_key = '{date}{histo_key}{sep}{ip_key}'.format(sep         = self.separator,\
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
    
    def get_daily_rank(self, asn, source = None, date = None):
        """
            Get the rank of an AS for a particular `source` and `date`
        """
        if source is None:
            source = self.config.get('input_keys','histo_global')
        if date is None:
            date = self.date
        return self.history_db.get(\
                    '{asn}{sep}{date}{sep}{source}{sep}{ip_key}'.format(sep     = self.separator,\
                                                                        asn     = asn,\
                                                                        date    = date,\
                                                                        source  = source,\
                                                                        ip_key  = self.ip_key))

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
        to_return_sources = set(()).union(*lists_sources)

        if sources is None:
            sources = to_return_sources
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
            return {}, to_return_sources
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
                        ranks_by_days[asn_day] = float(rank)
                    else:
                        ranks_by_days[asn_day] += float(rank)
                i += 1 
        for ranks in ranks_by_days:
            ranks_by_days[ranks] += 1 
        return ranks_by_days, to_return_sources
        
    def get_asn_descs(self, asn, sources = None, date = None):
        """
            Get the details of an ASN
        """
        if sources is None:
            sources = self.sources
        else:
            sources = [sources]
        if date is None:
            date = self.date
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
            nb_of_ips += sum(pipeline.execute())
            if nb_of_ips > 0:
                keys = ['{asn_timestamp_key}{owner}'.   format(asn_timestamp_key = asn_timestamp_key, \
                                                                           owner = self.config.get('input_keys','owner')),
                        '{asn_timestamp_key}{ip_block}'.format(asn_timestamp_key = asn_timestamp_key, \
                                                                        ip_block = self.config.get('input_keys','ips_block'))]
                owner, ip_block = self.global_db.mget(keys)
                sources_web = self.history_db_temp.smembers(asn_timestamp_temp)
                asn_descs_to_print.append([asn, timestamp, owner, ip_block, nb_of_ips, ', '.join(sources_web)])
        to_return = sorted(asn_descs_to_print, key=lambda desc: IP(desc[3]).len())
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
            date = self.date
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
