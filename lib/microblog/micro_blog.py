#!/usr/bin/python
# -*- coding: utf-8 -*-

import twitter
from micro_blog_keys import *

class MicroBlog():
    """
        Twitter client which inform the followers when something happens
        on BGP Ranking
    """
    
    def __init__(self):
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
        if len(string) <= 140:
            self.twitter_api.PostUpdate(string)
            self.identica_api.PostUpdate(string)
            return 0
        return 1
