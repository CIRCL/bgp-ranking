# -*- coding: utf-8 -*-

from db_models.ranking import *
from whois_parser.whois_parsers import *

import syslog
syslog.openlog('BGP_Ranking_Fetching_RIS', syslog.LOG_PID, syslog.LOG_USER)

import redis
import time

# Temporary redis database, used to push ris and whois requests
temp_reris_db = int(config.get('redis','temp_reris_db'))
# Cache redis database, used to set ris responses
ris_cache_reris_db = int(config.get('redis','ris_cache_reris_db'))

class FetchRIS():
    """
    Generate a ASNsDescriptions to all IPsDescriptions wich do not already have one.
    
    Take a look at doc/uml-diagramms/RIS\ Fetching.png to see a diagramm.
    """
    default_asn_desc = None
    max_loop = 3
    

    def __init__(self):
        """
        Initialize the two connectors to the redis server 
        """        
        self.cache_db_ris = redis.Redis(db=ris_cache_reris_db)
        self.temp_db = redis.Redis(db=temp_reris_db)

    def __commit(self):
        """
        Commit the pending modifications in the database 
        """
        r_session = RankingSession()
        r_session.commit()
        r_session.close()
    
    def __update_db_ris(self, current,  data):
        """ 
        Update the database with the RIS whois informations and return the corresponding entry
        """
        splitted = data.partition('\n')
        ris_origin = splitted[0]
        riswhois = splitted[2]
        ris_whois = Whois(riswhois,  ris_origin)
        if not ris_whois.origin:
            # the RIS whois entry is empty
            if not self.default_asn_desc:
                self.default_asn_desc = \
                    ASNsDescriptions(owner=unicode("IP without AS, see doc to know why"), \
                    ips_block=unicode('0.0.0.0'), asn=ASNs.query.get(unicode(-1)),  \
#                    whois=unicode('None'), whois_address=unicode('None'), \
                    riswhois_origin=unicode('None') )
            current.asn = self.default_asn_desc
        else:
            try:
                current_asn = ASNs.query.get(unicode(ris_whois.origin))
                if not current_asn:
                    # create a new ASN entry if it does not already exists
                    current_asn = ASNs(asn=unicode(ris_whois.origin))
                if not ris_whois.description:
                    # Sometimes, the descr field of the RIS Whois entry is empty
                    ris_whois.description = "This ASN has no description"
                asn_desc = ASNsDescriptions.query.filter_by(asn=current_asn, ips_block=unicode(ris_whois.route),\
                                                            owner=ris_whois.description.decode("iso-8859-1"),\
                                                            riswhois_origin=unicode(ris_origin)).first()
                if not asn_desc:
                    # Create a new ASNsDescriptions entry if there is anything new in the RIS Whois entry
                    asn_desc = ASNsDescriptions(asn=current_asn, ips_block=unicode(ris_whois.route), \
                                                owner=ris_whois.description.decode("iso-8859-1"), \
                                                riswhois_origin=unicode(ris_origin))
                current.asn = asn_desc
            except:
                syslog.syslog(syslog.LOG_ERR, 'Impossible to insert the ASN ' + ris_whois.origin + ', try again later.')
                time.sleep(sleep_timer)


    def get_ris(self, limit_first, limit_last):
        """
        Get the RIS whois information on a particular interval and put it into the MySQL database
        """
        self.ips_descriptions = IPsDescriptions.query.filter(IPsDescriptions.asn==None)[limit_first:limit_last]
        for ip_description in self.ips_descriptions:
            # push in a set of queries all the new requests
            if not self.cache_db_ris.exists(ip_description.ip.ip):
                self.temp_db.sadd(config.get('redis','key_temp_ris'),  ip_description.ip.ip)
        while len(self.ips_descriptions) > 0:
            """ 
            Put the RIS whois entries found in redis in the MySQL database. 
            
            Loop at most three times: this way the process is not blocked 
            if the RIS whois server takes a lot of time to answer.
            It it not a problem: if all the entries are not found, 
            the same process (or an other one) will try again later. 
            """
            deferred = []
            for description in self.ips_descriptions:
                entry = self.cache_db_ris.get(description.ip.ip)
                if not entry:
                    # entry not found, try again
                    deferred.append(description)
                else:
                    # entry found.
                    self.__update_db_ris(description, entry)
            self.ips_descriptions = deferred
            time.sleep(int(config.get('sleep_timers','short')))
            syslog.syslog(syslog.LOG_DEBUG, 'RIS Whois to fetch: ' + str(len(self.ips_descriptions)))
            self.max_loop -=1
            if self.max_loop <= 0:
                break
        self.__commit()
