#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
    Micro-blog
    ~~~~~~~~~~~~~
    
    Microblog client for twitter and identica
"""

import twitter
from micro_blog_keys import *
import sys
sys.path.append("/home/rvinot/bgp-ranking/lib/")

from helpers.common_report import CommonReport

class MicroBlog(CommonReport):
    """
        Twitter client which inform the followers when something happens
        on BGP Ranking
    """
    
    def __init__(self, ip_version = 4):
        CommonReport.__init__(self, ip_version)
        self.twitter_api = twitter.Api( consumer_key        =   twitter_customer_key,
                                        consumer_secret     =   twitter_consumer_secret,
                                        access_token_key    =   twitter_access_token_key,
                                        access_token_secret =   twitter_access_token_secret)
        self.identica_api = twitter.Api(consumer_key        =   identica_customer_key,
                                        consumer_secret     =   identica_consumer_secret,
                                        access_token_key    =   identica_access_token_key,
                                        access_token_secret =   identica_access_token_secret,
                                        base_url = 'https://identi.ca/api')

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
            to_return = 'Top Ranking {date}\n'.format(date = date)
            for report in reports:
                to_return += ''.join('{asn}: {rank}\n'.format(asn = report[0], rank = round(report[1]),2))
        return to_return

    def last_ranks_asn(self, asn):
        """
            Return all the rankings found in the DB for a given ASN
        """
        dates = self.get_dates()
        ranks = []
        values = ''
        for date in dates:
            rank = self.get_daily_rank(asn = asn, source = None, date = date)
            if rank is not None:
                values += ''.join('{date}: {rank}\n'.format(date = date, rank = round(rank,2)))
        if len(values) > 0:
            return '{asn}\n{values}'.format(asn = asn, values = values)
        return None

if __name__ == '__main__':
    from micro_blog import MicroBlog
    mb = MicroBlog()
    top = mb.top_date()
    mb.post(top)
#    print mb.last_ranks_asn(25489)