#!/usr/bin/python
# -*- coding: utf-8 -*-


"""
    Micro-blog
    ~~~~~~~~~~
    
    Microblog client for twitter and identica
    
    FIXME identica not completely implemented
"""

import twitter
from micro_blog_keys import *
import dateutil.parser
import redis

if __name__ == '__main__':
    import os
    import sys
    import ConfigParser
    config = ConfigParser.RawConfigParser()
    config_file = "/path/to/bgp-ranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

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
        self.microblog_db_temp = redis.Redis(port = int(self.config.get('redis','port_cache')),\
                                        db = self.config.get('redis','temp'))
        self.last_dm_twitter_key = "last_dm_twitter"
        self.last_dm_identica_key = "last_dm_identica"

    def grab_dms(self, api, key):
        last_dm_id = self.microblog_db_temp.get(key)
        if last_dm_id is None:
            dms = api.GetDirectMessages()
        else:
            dms = api.GetDirectMessages(since_id = last_dm_id)
            for dm in dms:
                data = dm.text.split()
                if len(data) > 0:
                    to_send = self.last_ranks_asn(*data)
                    if to_send is not None:
                        try:
                            api.PostDirectMessage(dm.sender_screen_name, to_send)
                        except:
                            pass
        if len(dms) > 0 :
            self.microblog_db_temp.set(key, dms[0].id)
    
    def post_last_top(self):
        last_top_date = self.check_last_top()
        raw_date, date = self.get_default_date()
        if date != last_top_date:
            self.post(self.top_date())
            return True
        return False

    def check_last_top(self):
        tl = self.twitter_api.GetUserTimeline("bgpranking")
        last_top_date = None
        for entry in tl:
            if "Top Ranking" in entry.text:
                last_top_date = entry.text.split()[2]
                break
        return last_top_date

    def post(self, string):
        """
            Post an entry in twitter and identi.ca
        """
        if len(string) <= 140:
            self.twitter_api.PostUpdate(string)
            self.identica_api.PostUpdate(string)
            return True
        return False
    
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
        if reports is not None and len(reports) > limit:
            to_return = 'Top Ranking {date}\n'.format(date = date)
            for report in reports:
                to_return += ''.join('{asn}: {rank}\n'.format(asn = report[0], rank = round(1 + report[1],3)))
        return to_return

    def last_ranks_asn(self, asn, source = None):
        """
            Return all the rankings found in the DB for a given ASN
        """
        dates = sorted(self.get_dates())
        ranks = []
        values = ''
        if source is None:
            source = self.config.get('input_keys','histo_global')
        for date in dates:
            rank = self.get_daily_rank_client(asn, date, source)
            if rank is not None:
                values += ''.join('{date}: {rank}\n'.format(date = date, rank = round(1 + rank,3)))
        if len(values) > 0:
            return '{asn} - {source}\n{values}'.format(asn = asn, source = source, values = values)
        return None

if __name__ == '__main__':
    from micro_blog import MicroBlog
    mb = MicroBlog()
    top = mb.top_date()
    mb.post(top)
#    print mb.last_ranks_asn(25489)
