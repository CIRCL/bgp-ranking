# -*- coding: utf-8 -*-

"""
Definition of the databases containing the ranking information.
"""

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

if __name__ == "__main__":
    engine = create_engine( 'mysql://' + login + ':' + password + '@' + host, pool_size = 50, pool_recycle=3600, max_overflow=30 )
    connection = engine.connect()
    connection.execute('CREATE DATABASE IF NOT EXISTS ' + dbname)
    connection = None

voting_engine = create_engine( 'mysql://' + login + ':' + password + '@' + host + '/' + dbname, pool_size = 50, pool_recycle=3600, max_overflow=30 )
VotingSession = scoped_session(sessionmaker(bind=voting_engine))
voting_metadata = ThreadLocalMetaData()
voting_metadata.bind = voting_engine
import datetime

import re

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
    histories = ManyToMany('History')
    using_options(metadata=voting_metadata, session=VotingSession, tablename='Votes')

class Sources(Entity):
    source = Field(Unicode(50), primary_key=True)
    histories = OneToMany('History')
    using_options(metadata=voting_metadata, session=VotingSession, tablename='Sources')
    

class History(Entity):
    """ 
    History of the rankings
    """
    asn = Field(Integer)
    timestamp = Field(DateTime(timezone=True), default=datetime.datetime.utcnow)
    rankv4 = Field(Float(precision=30), required=True)
    rankv6 = Field(Float(precision=30), required=True)
    votes = ManyToMany('Votes')
    source = ManyToOne('Sources')
    using_options(metadata=voting_metadata, session=VotingSession, tablename='History')

setup_all()
