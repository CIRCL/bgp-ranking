#!/usr/bin/python
# -*- coding: utf-8 -*-

import ConfigParser
import datetime
import redis

import constraints

global_db = None
history_db = None

# Tunnel: ssh crd -L 6379:crd:6379
hostname = '127.0.0.1'
dates = []
sources_by_dates = {}


def prepare():
    global global_db
    global history_db
    global dates
    global sources_by_dates
    config = ConfigParser.RawConfigParser()
    config.optionxform = str
    config_file = "/etc/bgpranking/bgpranking.conf"
    config.read(config_file)
    global_db = redis.Redis(port = int(config.get('redis','port_master')),
            db = config.get('redis','global'), host = hostname)
    history_db = redis.Redis(port = int(config.get('redis','port_master')),
            db = config.get('redis','history'), host = hostname)
    today = datetime.date.today()
    dates = [(today-datetime.timedelta(days=i)).isoformat()
                for i in range(constraints.last_days)]
    sources_by_dates = { date: global_db.smembers('{}|sources'.format(date))
                            for date in dates}
