#!/usr/bin/python

from abstract_init_whois_server import InitWhoisServer
import filecmp
import shutil

class InitRIPE(InitWhoisServer):

    keys =  [
        ['^inetnum:'    , [] ],
        ['^domain:'     , [] ],
        ['^inet6num:'   , [] ],
        ['^aut-num:'    , [] ],
        ['^route:'      , [] ],
        ['^route6:'     , [] ],
        ['^as-block:'   , [] ],
        ['^as-set:'     , [] ],
        ['^rtr-set:'    , [] ],
        ['^route-set:'  , [] ],
        ['^org:'        , [] ],
        ['^poetic-form:', [] ],
        ['^poem:'       , [] ],
        ['^peering-set:', [] ],
        ['^limerick:'   , [] ],
        ['^key-cert:'   , [] ],
        ['^inet-rtr:'   , [] ],
        ['^filter-set'  , [] ] ]

    archive_name = "ripe.db.gz"
    dump_name = "ripe.db"
    serial = "RIPE.CURRENTSERIAL"
    
    def __init__(self):
        InitWhoisServer.__init__(self)
        self.serial = os.path.join(whois_db,serial)
        self.last_parsed_serial = os.path.join(whois_db, serial + "_last")

    def new_file(self):
        if os.path.exists(last_parsed_serial) and filecmp.cmp(serial, last_parsed_serial):
            return False
        return True

    def  copy_serial(self):
        shutil.copy(self.serial,self.last_parsed_serial)
