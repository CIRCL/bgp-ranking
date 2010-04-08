#!/usr/bin/python
# -*- coding: utf-8 -*-
# Original Idea :
# =>  http://code.google.com/p/pywhois/source/browse/trunk/pywhois/parser.py

import re
from model import *
from .utils.ip_manip import ip_in_network
from socket import *

class AbstractWhois():
    """Abstract Class for parsing a Whois entry.
    ATTENTION: _whois_regs must be definded to say what we should search in the whois
    """
    server = None
    options =  ''
    port = 43
    
    def __fetch_whois(self):
        s = socket(AF_INET, SOCK_STREAM)
        s.connect((self.server,self.port))
        s.recv(1024)
        s.send(self.options + self.text + ' \n')
        self.text = s.recv(2048)
        s.close()

    # TODO: When we know the server, we know the _whois_regs to use 
    def __find_server(self):
        assignations = Assignations.query.all()
        for assignation in assignations:
            if ip_in_network(self.text, assignation.block):
                return assignation.whois


    def __init__(self, text, connect=True):
        self.text = text
        if connect: 
            if not self.server:
                self.server = self.__find_server()
            self.__fetch_whois()

    def __getattr__(self, attr):
        """The first time an attribute is called it will be calculated here.
        The attribute is then set to be accessed directly by subsequent calls.
        """
        whois_reg = self._whois_regs.get(attr)
        if whois_reg:
            value = re.findall(whois_reg, self.text)
            if not value:
                setattr(self, attr, None)
            else:
                setattr(self, attr, value[0])
            return getattr(self, attr)
        else:
            raise KeyError("Unknown attribute: %s" % attr)

    def __str__(self):
        """Print all whois properties of IP
        """
        return '\n'.join('%s: %s' % (attr, str(getattr(self, attr))) for attr\
               in self._whois_regs)
    
    def __repr__(self):
        return self.text
