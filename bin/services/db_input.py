#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
    :file:`bin/services/db_input.py` - Database Input
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Move the new entries from the incoming to the storage database
    Filter and sort the new entries given by the modules.
    Ensure that:

    * the entry is valid: has an IP and a source
    * the entry is not already here
"""

import ConfigParser
import time

from pubsublogger import publisher

import datetime
import dateutil.parser
import redis

import IPy

uid_list = "uid_list"
list_ips = 'ips'
list_sources = 'sources'
separator = '|'
key_ip = 'ip'
key_src = 'source'
key_tstamp = 'timestamp'

temp_ris = 'ris'
temp_no_asn = 'no_asn'

sleep_timer = 10


accept_old_entries = False

stop_db_input = 'stop_db_input'

temp_db = None
global_db = None
config_db = None

def prepare():
    """
        Connection to the redis instances
    """
    global temp_db
    global global_db
    global config_db
    config = ConfigParser.RawConfigParser()
    config_file = '/etc/bgpranking/bgpranking.conf'
    config.read(config_file)
    temp_db    = redis.Redis(port = int(config.get('redis','port_cache')),
                        db=int(config.get('modules_global','temp_db')))
    global_db  = redis.Redis(port = int(config.get('redis','port_master')),
                        db=int(config.get('redis','global')))
    config_db = redis.Redis(port = int(config.get('redis','port_master')),
                        db = config.get('redis','config'))
    config_db.delete(stop_db_input)

def get_all_information():
    """
        Extract from the database all the information provided by the modules.
    """
    uid = temp_db.spop(uid_list)
    if uid is None:
        return None

    table_keys = [key_ip, key_src, key_tstamp]

    ip, src, timestamp = temp_db.hmget(uid, table_keys)
    if timestamp is None:
        timestamp = datetime.date.today()
    else:
        timestamp = dateutil.parser.parse(timestamp)
    return uid, ip, src, timestamp

def insert():
    """
        Re-insert in the database the data provided by the module and
        extracted by :meth:`get_all_information` in a sorted form.
    """
    while True:
        i = 0
        try:
            while temp_db.scard(uid_list) > 0:
                infos = get_all_information()
                if infos is None:
                    continue
                uid, ip, src, timestamp = infos
                if ip is None:
                    publisher.error('Entry without IP, invalid')
                    continue
                if src is None:
                    publisher.error(ip + ' without source, invalid')
                    continue
                if timestamp.date() < datetime.date.today() and not accept_old_entries:
                    publisher.warning('The timestamp ({ts}) of {ip} from {source} is too old.'.\
                            format(ts = timestamp.isoformat(), ip = ip, source = src))
                    continue
                try:
                    # Check and normalize the IP
                    ip_bin = IPy.IP(ip)
                    if ip_bin.iptype() != 'PUBLIC':
                        publisher.warning(str(ip_bin) + ' is not a PUBLIC IP Address')
                        continue
                    ip = ip_bin.strCompressed()
                except:
                    publisher.error('This IP: ' + ip + ' in invalid.')
                    continue

                iso_timestamp = timestamp.isoformat()
                date = timestamp.date().isoformat()
                index_day_src = '{date}{sep}{key}'.format(sep = separator,
                        date=date, key=list_sources)
                index_day_ips = 'temp{sep}{date}{sep}{source}{sep}{key}'.format(
                        sep = separator, date=date, source=src, key=list_ips)
                ip_details = '{ip}{sep}{timestamp}'.format(sep = separator,
                        ip = ip, timestamp = iso_timestamp)

                global_db.sadd(index_day_src, src)
                pipeline_temp_db = temp_db.pipeline()
                pipeline_temp_db.sadd(index_day_ips, ip_details)
                pipeline_temp_db.sadd(temp_ris, ip)
                pipeline_temp_db.sadd(temp_no_asn, index_day_ips)
                pipeline_temp_db.delete(uid)
                pipeline_temp_db.execute()
                i += 1
                if i%100 == 0 and config_db.exists(stop_db_input):
                    break
                if i%10000 == 0:
                    publisher.info('{nb} new entries to insert'\
                            .format(nb = temp_db.scard(uid_list)))
        except:
            publisher.critical('Unable to insert, redis does not respond')
            break
        time.sleep(sleep_timer)
        if config_db.exists(stop_db_input):
            publisher.info('DatabaseInput stopped.')
            break


def stop_services(signum, frame):
    """
        Set a value in redis to quit the loop properly
    """
    config = ConfigParser.RawConfigParser()
    config_file = "/etc/bgpranking/bgpranking.conf"
    config.read(config_file)
    config_db = redis.Redis(port = int(config.get('redis','port_master')),
            db = config.get('redis','config'))
    config_db.set(stop_db_input, 1)


if __name__ == '__main__':
    import signal

    publisher.channel = 'DatabaseInput'
    publisher.info('DatabaseInput started.')
    signal.signal(signal.SIGHUP, stop_services)
    prepare()
    insert()
