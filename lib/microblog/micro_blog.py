#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
    Micro-blog
    ~~~~~~~~~~~~~
    
    Microblog client for twitter and identica
"""

import twitter
from micro_blog_keys import *
from helpers.common_values import CommonValues

class MicroBlog(CommonReport):
    """
        Twitter client which inform the followers when something happens
        on BGP Ranking
    """
    
    def __init__(self, ip_version = 4):
        CommonReport.__init__(self, ip_version)

    def post(self, string):
        """
            Post an entry in twitter and identi.ca
        """
        if len(string) <= 140:
            self.twitter_api.PostUpdate(string)
            self.identica_api.PostUpdate(string)
            return 0
        return 1
    
    def top_date(self, date = None):
        """
            Return the top ASN for a given date
        """
        if date is None:
            raw_date, date = self.get_default_date()
        source = self.config.get('input_keys','histo_global')
        histo_key = '{date}{sep}{histo_key}{sep}{ip_key}'.format(   sep         = self.separator,\
                                                                    date        = date,\
                                                                    histo_key   = source,\
                                                                    ip_key      = self.ip_key)
        limit = 5
        reports = self.history_db_temp.zrevrange(histo_key, 0, limit, True)
        to_return = None
        if reports is not None:
            to_return = ''
            for report in reports:
                to_return.join('{asn}: {rank}\n'.format(asn = report[0], rank = report[1]))
        return to_return

    def last_ranks_asn(self, asn):
        """
            Return all the rankings found in the DB for a given ASN
        """
        dates = common_values.get_dates()
        ranks = []
        values = ''
        for date in dates:
            rank = self.get_daily_rank(asn = asn, source = None, date = date)
            if rank is not None:
                values.join('{date}: {rank}\n'.format(date = date, rank = rank))
        if len(values) > 0:
            return '{asn}\n{values}'.format(asn = asn, values = values)
        return None