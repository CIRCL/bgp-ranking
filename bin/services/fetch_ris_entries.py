#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

    :file:`bin/services/fetch_ris_entries.py` - Fetch the RIS RIPE entries
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Fetch the whois entries from a whois server.
"""

import ConfigParser
import socket

import redis

import time

from pubsublogger import publisher
import argparse

sleep_timer = 10
# Set the ttl of the cached entries to 1 day
cache_ttl = 86400

temp_db = None
cache_db = None

keepalive = True

server = None
port = 43

server_socket = None
connected = False

key_ris = 'ris'

def prepare():
    """
        Set variables depending on the server, initialize a :class:`WhoisFetcher` on this server
    """
    global temp_db
    global cache_db
    global fetcher

    config = ConfigParser.RawConfigParser()
    config_file = "/etc/bgpranking/bgpranking.conf"
    config.read(config_file)


    temp_db = redis.Redis(port = int(config.get('redis','port_cache')),
            db=int(config.get('redis','temp')))
    cache_db = redis.Redis(port = int(config.get('redis','port_cache')),
            db=int(config.get('redis','cache_ris')))

def __connect():
    """
        Connect the :class:`WhoisFetcher` instance
    """
    global connected
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((server,port))
    # Skip the welcome message
    server_socket.recv(1024)
    connected = True

def __disconnect():
    """
        Disconnect the :class:`WhoisFetcher` instance
    """
    global connected
    if server_socket is not None:
        server_socket.close()
    connected = False

def fetch_whois(query):
    """
        Fetch the RIS RIPE informations. Keep the connection is possible.
    """
    server_socket.send('-k ' + query + '\n')
    text = ''
    fs = server_socket.makefile()
    prec = ''
    while 1:
        temp = fs.readline()
        if not temp or len(temp) == 0 or prec == temp == '\n':
            break
        text += temp
        prec = temp
    if len(text) == 0:
        publisher.error("error (no response) with query: " + query +
                " on server " + server)
        time.sleep(sleep_timer)
    if not keepalive:
        __disconnect()
    return text



def launch():
    """
        Fetch all the whois entry assigned to the server of this :class:`Connector`
    """
    i = 0
    while True:
        try:
            entry = temp_db.spop(key_ris)
            if not entry:
                __disconnect()
                i = 0
                publisher.debug("Disconnected of " + server)
                time.sleep(sleep_timer)
                continue
            if cache_db.get(entry) is None:
                if not connected:
                    __connect()
                publisher.debug(server + ", query : " + str(entry))
                whois = fetch_whois(entry)
                if whois != '':
                    cache_db.setex(entry, server + '\n' + unicode(whois,  errors="replace"), cache_ttl)
                if not keepalive:
                    __disconnect()
            i += 1
            if i%10000 == 0:
                publisher.info(str(temp_db.scard(key_ris)) + ' to process on ' + server)
        except IOError as text:
            publisher.error("IOError on " + server + ': ' + str(text))
            time.sleep(sleep_timer)
            __disconnect()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Start a RISWhois fetcher.')
    parser.add_argument("-s", "--server", required=True, type=str, help='Hostname of the Whois server.')
    args = parser.parse_args()

    publisher.channel = 'RISWhoisFetch'
    server = args.server
    prepare()
    launch()
