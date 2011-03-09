#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    
    :file:`bin/services/fetch_whois_entries.py` - Fetch the Whois entries
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Launch a connector which fetch the whois entries 
    on a particular whois server.
"""


def usage():
    print "whois_fetching.py server.tld"
    exit (1)


if __name__ == '__main__':
    
    import os 
    import sys
    import ConfigParser
    config = ConfigParser.RawConfigParser()
    config_file = "/path/to/bgp-ranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,config.get('directories','libraries')))

    from whois_client.connector import Connector

    if len(sys.argv) < 2:
        usage()

    c = Connector(sys.argv[1])
    c.launch()
