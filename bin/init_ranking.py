#!/usr/bin/python
# -*- coding: utf-8 -*-

from utils.models import *

ranking_metadata.drop_all()
ranking_metadata.create_all()

# Creation of the "default AS", see fetch_asn.py for more informations 
ASNs(asn=unicode('-1'))

r_session = RankingSession()
r_session.commit()
r_session.close()
