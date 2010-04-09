# http://bazaar.launchpad.net/~ubuntu-branches/ubuntu/lucid/whois/lucid/files
# to get the address assignations

from elixir import *

metadata.bind = "sqlite:///ranking.sqlite"
metadata.bind.echo = True

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
    pre_options = Field(UnicodeText, default='')
    post_options = Field(UnicodeText, default='')
    port = Field(Integer, default=43)

    def __repr__(self):
        return 'Block: "%s\t Whois Server: %s"' % (self.block, self.whois)


setup_all()
create_all()


