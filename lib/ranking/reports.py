#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    Reports
    ~~~~~~~

    Model used by the website to get information from the database (read only)
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

    def get_sources(self, date):
        """
            Get the sources parsed on a `date`
        """
        if date is None:
            # Fallback if no date is given in the web interface
            date = self.get_default_date()[1]
        return super(Reports, self).get_sources(date)

    def format_report(self, source, date, limit = 50):
        """
            Format the report to be displayed in the website
        """
        if source is None:
            source = self.config.get('input_keys','histo_global')
        if date is None:
            date = self.get_default_date()[1]
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
        return [ [ x[0], x[1], list(y)] for x,y in zip(reports_temp,sources)]

    def get_asn_descs(self, graph_first_date, graph_last_date, asn, sources, date):
        """
            Get the details of an ASN
        """
        timestamps = self.global_db.smembers(asn)
        if len(timestamps) == 0:
            # The ASN does not exists in the database
            return [], [], []

        if date is None:
            date = self.get_default_date()[1]
        if sources is None:
            sources = self.get_sources(date)
        else:
            sources = [sources]

        # generate a list of dates
        graph_dates = self.get_dates_from_interval(graph_first_date, graph_last_date)
        if len(sources) == 1:
            dates_sources = dict.fromkeys(graph_dates, sources)
            # python 2.7 only:
            #dates_sources = {date: sources[0] for date in graph_dates}
        else:
            # get all the sources available, by date: { day: [source1, source2...}, ...}
            dates_sources = self.get_all_sources(graph_dates)
        all_ranks = self.get_all_ranks(asn, graph_dates, dates_sources)
        # Compute the data to display in the graph
        data_graph, last_seen_sources = self.prepare_graphe_js(all_ranks, graph_dates, dates_sources)

        asn_descs_to_print = []
        for timestamp in timestamps:
            # Get the number of IPs found in the database for each subnet
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
                impacts = self.config_db.mget(sources)
                # Compute the local ranking: the ranking if this subnet is the only one for this AS
                local_rank = sum([ float(ips_by_sources[i]) * float(impacts[i]) for i in range(len(sources)) ]) / IP(ip_block).len()

                asn_timestamp_temp = '{date}{sep}{asn}{sep}{timestamp}'.format(\
                                                    sep = self.separator, date      = date,\
                                                    asn = asn,            timestamp = timestamp)
                sources_web = self.history_db_temp.smembers(asn_timestamp_temp)
                asn_descs_to_print.append( [asn, timestamp, owner, ip_block, nb_of_ips, sources_web, local_rank] )
        to_return = sorted(asn_descs_to_print, key=lambda desc: desc[6], reverse = True)
        return to_return, last_seen_sources, data_graph

    def daterange(self, start, end, delta):
        """
            Just like `range`, but for dates!
            origin: http://stackoverflow.com/questions/1950098/does-python-have-any-for-loop-equivalent-not-foreach
        """
        current = start
        while current <= end:
            yield current
            current += delta

    def get_dates_from_interval(self, first_date, last_date):
        """
            Generate a list of dates between first_date and  last_date
            with this format: YYYY-MM-DD
        """
        return [ d.strftime("%Y-%m-%d") for d in self.daterange(first_date, last_date, datetime.timedelta(days=1))]

    def get_all_sources(self, dates):
        """
            Return a list of sources available for all the dates.
            { day: [source1, source2...}, ...}
        """
        pipeline = self.global_db.pipeline()
        for date in dates:
            pipeline.smembers(\
                '{date}{sep}{key}'.format(  date    = date,\
                                            sep     = self.separator,\
                                            key     = self.config.get('input_keys','index_sources')))

        lists_sources = pipeline.execute()
        return dict(zip(dates,lists_sources))

    def get_all_ranks(self, asn, dates, dates_sources):
        """
            Return all the ranks of an ASN for all the dates and all the sources:
                { 'Source1' : [rank_day1, rank_day_2, ...], ...}
                Note: it there is no rank for a day, rank_day_X will be None
        """
        keys = {}
        pipeline = self.history_db.pipeline()
        for date in dates:
            sources = dates_sources[date]
            if len(sources) > 0:
                string = '{asn}{sep}{date}{sep}{source}{sep}{v4}'
                # Generate the list of keys to mget
                keys[date] = [ string.format(\
                                        sep  = self.separator, asn     = asn,\
                                        date = date,           source  = source,\
                                        v4   = self.config.get('input_keys','rankv4'))
                                    for source in sources]
                pipeline.mget(keys[date])
        histories = pipeline.execute()
        if len(histories) == 0:
            # Nothing to display, quit
            return []
        return histories

    def prepare_graphe_js(self, ranks, dates, dates_sources):
        """
            Prepare the data to display in the graph
        """
        ranks_by_days = {}
        last_seen_sources = {}
        i = 0
        for date in dates:
            # get all the sources for a date
            sources = dates_sources[date]
            if len(sources) > 0:
                ranks_by_days[date] = 0
                # Get all the ranks for the day
                daily_ranks = ranks[i]
                j = 0
                for source in sources:
                    rank = daily_ranks[j]
                    if rank is not None:
                        last_seen_sources[source] = date
                        ranks_by_days[date] += float(rank) * float(self.config_db.get(str(source)))
                    j += 1
                i += 1
            else:
                # no sources for the day
                ranks_by_days[date] = None
        return ranks_by_days, last_seen_sources

    def get_ips_descs(self, asn, asn_timestamp, sources, date):
        """
            Get the details of a subnet
        """
        if date is None:
            date = self.get_default_date()[1]
        if sources is None:
            sources = self.get_sources(date)
        else:
            sources = [sources]

        asn_timestamp_key = '{asn}{sep}{timestamp}{sep}'.format(asn = asn, sep = self.separator, timestamp = asn_timestamp)
        pipeline = self.global_db.pipeline()
        for source in sources:
            pipeline.smembers('{asn_timestamp_key}{date}{sep}{source}'.format(sep = self.separator, \
                                        asn_timestamp_key = asn_timestamp_key, date = date, source=source))
        ips_by_source = pipeline.execute()
        if len(ips_by_source) == 0:
            return []
        ip_descs_to_print = {}
        i = 0
        for source in sources:
            ips = ips_by_source[i]
            for ip_details in ips:
                ip, timestamp = ip_details.split(self.separator)
                if ip_descs_to_print.get(ip) is None:
                    ip_descs_to_print[ip] = [source]
                else:
                    ip_descs_to_print[ip].append(source)
            i += 1
        return sorted(ip_descs_to_print.items(), key=lambda desc: (len(desc[1]), IP(desc[0]).int()), reverse=True)

    def get_stats(self):
        """
            Return stats by sources:
            { Source : [nb_asns, nb_subnets]...}
        """
        dates = self.get_dates()
        to_return = {}
        for date in dates:
            to_return[date] = {}
            sources = self.get_sources(date)
            for source in sources:
                to_return[date][source] = []
                to_return[date][source].append(self.history_db_temp.zcard(\
                                                '{date}{sep}{histo_key}{sep}{ip_key}'.format(\
                                                    sep         = self.separator,\
                                                    date        = date,\
                                                    histo_key   = source,\
                                                    ip_key      = self.ip_key)))
                to_return[date][source].append(self.global_db.scard(\
                                        '{date}{sep}{source}{sep}{key}'.format(\
                                            date = date, sep = self.separator, source = source,\
                                            key = self.config.get('input_keys','index_asns_details'))))
        return to_return

    def get_stats_asns(self):
        """
            Return stats by sources:
            { Source : [nb_asns, nb_subnets]...}
        """
        dates = self.get_dates()
        max_nr = 0
        to_return = {}
        for date in dates:
            to_return[date] = {}
            sources = self.get_sources(date)
            for source in sources:
                to_return[date][source] = self.history_db_temp.zcard(\
                                                '{date}{sep}{histo_key}{sep}{ip_key}'.format(\
                                                    sep         = self.separator,\
                                                    date        = date,\
                                                    histo_key   = source,\
                                                    ip_key      = self.ip_key))
                max_nr = max(max_nr, to_return[date][source])
        return to_return, max_nr

    def prepare_distrib_graph(self, date):
        """
            Prepate the distributions graph printed using RGaph
        """
        source = self.config.get('input_keys','histo_global')
        histo_key = '{date}{sep}{histo_key}{sep}{ip_key}'.format(   sep         = self.separator,\
                                                            date        = date,\
                                                            histo_key   = source,\
                                                            ip_key      = self.ip_key)

        reports_temp = self.history_db_temp.zrevrange(histo_key, 0, -1, True)
        report_rounded = [ '%.3f' % round( 1 + r[1],3) for r in reports_temp ]
        unique_set = set(rank for rank in report_rounded)
        to_return = {}
        # FIXME python 2.7
        for rank in unique_set:
            to_return[rank] = report_rounded.count(rank)
        return to_return

    def prepare_distrib_graph_protovis(self, dates):
        """
            Prepare the data used to display statististics using ProtoVis
        """
        source = self.config.get('input_keys','histo_global')
        to_return = {}
        for date in dates:
            histo_key = '{date}{sep}{histo_key}{sep}{ip_key}'.format(   sep         = self.separator,\
                                                                date        = date,\
                                                                histo_key   = source,\
                                                                ip_key      = self.ip_key)

            reports_temp = self.history_db_temp.zrevrange(histo_key, 0, -1, True)
            report_rounded = [ '%.3f' % round( 1 + r[1],3) for r in reports_temp ]
            unique_set = set(rank for rank in report_rounded)
            for rank in unique_set:
                if to_return.get(rank) is None:
                    to_return[rank] = {}
                to_return[rank][date] = report_rounded.count(rank)
        return to_return
