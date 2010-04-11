# -*- coding: utf-8 -*-
from model import *

whois_metadata.bind = whois_engine
whois_session.bind = whois_engine

setup_all()
whois_metadata.create_all()
