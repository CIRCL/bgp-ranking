# -*- coding: utf-8 -*-
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
dbname = config.get('mysql','dbname_voting')
os.chdir(precdir) 

voting_engine = create_engine( 'mysql://' + login + ':' + password + '@' + host + '/' + dbname, pool_size = 50, pool_recycle=7200, max_overflow=30 )
VotingSession = scoped_session(sessionmaker(bind=voting_engine))
voting_metadata = ThreadLocalMetaData()
voting_metadata.bind = voting_engine
import re

import datetime

class Users(Entity):
    """ 
    Users
    """
    login = Field(UnicodeText, required=True)
    password = Field(UnicodeText, required=True)
    using_options(metadata=voting_metadata, session=VotingSession, tablename='Users')
    votes = OneToMany('Votes')

    def __repr__(self):
        return 'Login: "%s"\t Password: "%s"' % (self.login, self.password)

class Votes(Entity):
    """ 
    Votes
    """
    vote = Field(Integer, required=True)
    commentary = Field(UnicodeText, required=True)
    asn = Field(Integer, required=True)
    user = ManyToOne('Users')
    using_options(metadata=voting_metadata, session=VotingSession, tablename='Votes')

class History(Entity):
    """ 
    History of the rankings
    """
    asn = Field(Integer, primary_key=True)
    timestamp = Field(DateTime(timezone=True), default=datetime.datetime.utcnow, primary_key=True)
    rankv4 = Field(Float, required=True)
    rankv6 = Field(Float, required=True)
    votes = Field(UnicodeText) # user_id:vote;user_id:vote;user_id:vote;user_id:vote;user_id:vote;...
    using_options(metadata=voting_metadata, session=VotingSession, tablename='History')

setup_all()
