# -*- coding: utf-8 -*-
# http://bazaar.launchpad.net/~ubuntu-branches/ubuntu/lucid/whois/lucid/files
# to get the address assignations
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from elixir import *


whois_engine = create_engine("sqlite:///whois.sqlite") #, echo=True)
whois_session = scoped_session(sessionmaker())
whois_metadata = metadata

__metadata__ = whois_metadata
__session__ = whois_session

whois_metadata.bind = whois_engine
whois_session.bind = whois_engine


#metadata.bind = "sqlite:///ranking.sqlite"
#metadata.bind.echo = True

import re

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

INET6_ADDRSTRLEN = 46

class Assignations(Entity):
    """ 
    Ip assignations
    """
    block = Field(Unicode(INET6_ADDRSTRLEN), primary_key=True)
    whois = Field(UnicodeText, required=True)
    pre_options = Field(UnicodeText, default=unicode(''))
    post_options = Field(UnicodeText, default=unicode(''))
    port = Field(Integer, default=43)

    def __repr__(self):
        return 'Block: "%s\t Whois Server: %s"' % (self.block, self.whois)
