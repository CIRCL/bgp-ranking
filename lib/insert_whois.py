# -*- coding: utf-8 -*-
"""
    bgp_ranking.lib.InsertWhois
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Insert the Whois information in the database.

"""
import redis
import time
import os
import sys
import ConfigParser
import syslog

class InsertWhois(object):
    """
    Set the whois information to ASNsDescriptions wich do not already have one.

    Take a look at doc/uml-diagramms/Whois\ Fetching.png to see a diagramm.
    """
    max_consecutive_errors = 10

    def __init__(self):
        """
        Initialize the two connectors to the redis server
        """
        syslog.openlog('BGP_Ranking_Fetching_Whois', syslog.LOG_PID, syslog.LOG_LOCAL5)

        self.config= ConfigParser.RawConfigParser()
        config_file = "/path/to/bgp-ranking.conf"
        self.config.read(config_file)

        self.separator = self.config.get('input_keys','separator')

        self.key_whois = self.config.get('input_keys','whois')
        self.key_whois_server = self.config.get('input_keys','whois_server')

        self.cache_db   = redis.Redis(port = int(self.config.get('redis','port_cache')),\
                                        db=int(self.config.get('redis','cache_whois')))
        self.global_db  = redis.Redis(port = int(self.config.get('redis','port_master')),\
                                        db=int(self.config.get('redis','global')))

    def get_whois(self):
        """
        Get the Whois information on a particular interval and put it into redis
        """
        key_no_whois = self.config.get('redis','no_whois')
        description = self.cache_db.spop(key_no_whois)
        errors = 0
        to_return = False

        syslog.syslog(syslog.LOG_DEBUG, 'Whois to fetch: ' + str(self.global_db.scard(key_no_whois)))
        while description is not None:
            ip, timestamp = description.split(self.separator)
            entry = self.cache_db.get(ip)
            if entry is None:
                errors += 1
                self.cache_db.sadd(key_no_whois, description)
                if errors >= self.max_consecutive_errors:
                    break
            else:
                errors = 0
                splitted = entry.partition('\n')
                whois_server = splitted[0]
                whois = splitted[2]
                # FIXME: msetex ? (mset + expire
                self.global_db.set("{entry}{sep}{whois_server}".format(entry = entry, \
                                    sep = self.separator, whois_server = self.key_whois_server), \
                                    whois_server)
                self.global_db.set("{entry}{sep}{whois}".format(entry = entry,sep = self.separator, whois = self.key_whois), whois)
                to_return = True
            description = self.cache_db.spop(key_no_whois)
        syslog.syslog(syslog.LOG_DEBUG, 'Whois to fetch: ' + str(self.global_db.scard(key_no_whois)))
        return to_return
