# -*- coding: utf-8 -*-
# http://bazaar.launchpad.net/~ubuntu-branches/ubuntu/lucid/whois/lucid/files
# to get the address assignations
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.schema import ThreadLocalMetaData
from elixir import *

whois_engine = create_engine('mysql://root@localhost/whois')
whois_metadata = ThreadLocalMetaData()
__metadata__ = whois_metadata

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

    def __repr__(self):
        return 'Block: "%s\t Whois Server: %s"' % (self.block, self.whois)
