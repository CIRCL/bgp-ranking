#!/usr/bin/python
# -*- coding: utf-8 -*-

import twitter

class MyTwitterClient():
    """
        Twitter client which inform the followers when something happens
        on BGP Ranking
    """
    
    customer_key =  'XXXX'
    consumer_secret = 'XXXX'
    access_token_key = 'XXXX'
    access_token_secret = 'XXXX'
    
    def __init__(self):
        api = twitter.Api(  consumer_key        =   customer_key, 
                            consumer_secret     =   consumer_secret,
                            access_token_key    =   access_token_key,
                            access_token_secret =   access_token_secret)

    def post(self, string):
        if len(string) <= 140:
            api.PostUpdate(string)
            return 0
        return 1
