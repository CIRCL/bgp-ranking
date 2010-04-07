# http://bazaar.launchpad.net/~ubuntu-branches/ubuntu/lucid/whois/lucid/files
# to get the address assignations


import re
from elixir import *
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

metadata.bind = "sqlite:///whois.sqlite"
#metadata.bind.echo = True
INET6_ADDRSTRLEN = 46

class Assignations(Entity):
    """ 
    Ip assignations
    """
    block = Field(Unicode(INET6_ADDRSTRLEN), primary_key=True)
    whois = Field(UnicodeText, required=True)

    def __repr__(self):
        return 'Block: "%s\t Whois Server: %s"' % (self.block, self.whois)

setup_all()


