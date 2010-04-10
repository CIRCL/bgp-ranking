# -*- coding: utf-8 -*-
from models import *

ranking_metadata.bind = ranking_engine
ranking_session.bind = ranking_engine

setup_all()
create_all()

# Creation of the "default AS", see fetch_asn.py for more informations 
if not ASNs.query.get(unicode('-1')):
    ASNs(asn=unicode('-1'))
    ranking_session.commit()
