# -*- coding: utf-8 -*-

"""
Definition of the database containing the assignations. 

FIXME: not used anymore, drop it! 
"""


from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.schema import ThreadLocalMetaData
from elixir import *

import os
precdir = os.path.realpath(os.curdir)
os.chdir(os.path.dirname(__file__))
import ConfigParser
config = ConfigParser.RawConfigParser()
config.optionxform = str
config.read("../../etc/bgp-ranking.conf")
login = config.get('mysql','login')
password = config.get('mysql','password')
host = config.get('mysql','hostname')
dbname = config.get('mysql','dbname_whois')
os.chdir(precdir) 

whois_engine = create_engine( 'mysql://' + login + ':' + password + '@' + host + '/' + dbname )
WhoisSession = scoped_session(sessionmaker(bind=whois_engine))
whois_metadata = ThreadLocalMetaData()
whois_metadata.bind = whois_engine
import re

INET6_ADDRSTRLEN = 46

class Assignations(Entity):
    """ 
    Ip assignations
    """
    block = Field(Unicode(INET6_ADDRSTRLEN), default=unicode(''))
    whois = Field(UnicodeText, required=True)
    pre_options = Field(UnicodeText, default=unicode(''))
    post_options = Field(UnicodeText, default=unicode(''))
    keepalive_options = Field(UnicodeText, default=unicode(''))
    port = Field(Integer, default=43)
    using_options(metadata=whois_metadata, session=WhoisSession, tablename='Assignations')

    def __repr__(self):
        return 'Block: "%s"\t Whois Server: "%s"' % (self.block, self.whois)

setup_all()
