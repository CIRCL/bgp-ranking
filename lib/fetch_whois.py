# -*- coding: utf-8 -*-

from db_models.ranking import *
from helpers.ip_manip import ip_in_network
from whois_parser.whois_parsers import *

import syslog
syslog.openlog('BGP_Ranking_Fetching_Whois', syslog.LOG_PID, syslog.LOG_USER)

import redis
import time

# Temporary redis database, used to push ris and whois requests
temp_reris_db = int(config.get('redis','temp_reris_db'))
# Cache redis database, used to set whois responses
whois_cache_reris_db = int(config.get('redis','whois_cache_reris_db'))

class FetchWhois():
    """
    Set the whois information to ASNsDescriptions wich do not already have one.
    
    Take a look at doc/uml-diagramms/Whois\ Fetching.png to see a diagramm.
    """
    max_loop = 3
    

    def __init__(self):
        """
        Initialize the two connectors to the redis server 
        """
        self.cache_db_whois = redis.Redis(db=whois_cache_reris_db)
        self.temp_db = redis.Redis(db=temp_reris_db)

    def __commit(self):
        """
        Commit the pending modifications in the database 
        """
        r_session = RankingSession()
        r_session.commit()
        r_session.close()


    def get_whois(self, limit_first, limit_last):
        """
        Get the whois information on a particular interval and put it into the MySQL database
        """
        self.ips_descriptions = IPsDescriptions.query.filter(IPsDescriptions.whois==None)[limit_first:limit_last]
        for ip_description in self.ips_descriptions:
            # push in a set of queries all the new requests
            if not self.cache_db_whois.exists(ip_description.ip.ip):
                self.temp_db.sadd(config.get('redis','key_temp_whois'),  ip_description.ip.ip)
        while len(self.ips_descriptions) > 0:
            """ 
            Put the whois entries found in redis in the MySQL database. 
            
            Loop at most three times: this way the process is not blocked 
            if a whois server takes a lot of time to answer.
            It it not a problem: if all the entries are not found, 
            the same process (or an other one) will try again later. 
            """
            deferred = []
            for description in self.ips_descriptions:
                entry = self.cache_db_whois.get(description.ip.ip)
                if not entry:
                    # entry not found, try again
                    deferred.append(description)
                else:
                    # entry found. The first line is the whois server which answered
                    splitted = entry.partition('\n')
                    description.whois_address = unicode(splitted[0])
                    description.whois = unicode(splitted[2], errors="ignore")
            self.ips_descriptions = deferred
            time.sleep(int(config.get('sleep_timers','short')))
            syslog.syslog(syslog.LOG_DEBUG, 'Whois to fetch: ' + str(len(self.ips_descriptions)))
            self.max_loop -=1
            if self.max_loop <= 0:
                break
        self.__commit()
