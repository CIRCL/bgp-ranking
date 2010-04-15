# -*- coding: utf-8 -*-

from models import *

ranking_session = scoped_session(sessionmaker(bind=ranking_engine))
ranking_metadata.bind = ranking_engine

__session__ = ranking_session

setup_all()
#ranking_metadata.drop_all()
ranking_metadata.create_all()

# Creation of the "default AS", see fetch_asn.py for more informations 
if not ASNs.query.get(unicode('-1')):
    ASNs(asn=unicode('-1'))
    ranking_session.commit()

ranking_session.close()
