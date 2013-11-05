#!/usr/bin/python
# -*- coding: utf-8 -*-

"""

    Push routing dump and compute ranking
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    This script has two parts:

     1. pushing the routing information in a database
     2. computing the ranking using the routing information

    This way, we ensure of the integrity of the routing information.

    .. note::
     1. To push the routing information we have first to generate a
        plain text file from the binary dump. The second part use the
        splitting module to make a certain number of files (defined in
        the configuration file). When it is finished, the process start
        a process on each files to push the information into redis.
        And wait that each process is finished.

     2. It manages a pool of processes computing the ranking.
        Using the number of processes defined in the config file, the
        interval assigned to each process is computed.
"""

import os
import sys
import ConfigParser
from subprocess import Popen, PIPE
import time
import redis
import datetime
import IPy

from pubsublogger import publisher

path_bviewtimesamp = 'bgp/bview.gz.timestamp'
path_bviewfile = 'bgp/bview.gz'
bview_check_interval = 3600
sleep_timer = 10
path_to_bgpdump_bin = 'thirdparty/bgpdump/bgpdump'
days_history_cache = 3

key_to_rank = 'to_rank'
number_of_splits = 10
split_procs = 10
rank_procs = 10


def intervals_ranking(nb_of_asns, interval):
    """
        Compute the size of each intervals based on the number of ASNs
        found in the database and the number of processes defined in
        the configuration file
    """
    first = 0
    intervals = []
    while first < nb_of_asns:
        intervals.append(str(first) + ' ' + str(first + interval))
        first += interval + 1
    return intervals

def run_splitted_processing(max_sim_procs, process_name, process_args):
    """
        Run processes which push the routing dump of the RIPE in a
        redis database. The dump has been splitted in multiple files
        and each process run on one of this files.
    """
    pids = []
    while len(process_args) > 0:
        while len(process_args) > 0 and len(pids) < max_sim_procs:
            arg = process_args.pop()
            pids.append(service_start(servicename = process_name,
                param = ['-f', arg]))
        while len(pids) == max_sim_procs:
            time.sleep(sleep_timer)
            pids = update_running_pids(pids)
    while len(pids) > 0:
        # Wait until all the processes are finished
        time.sleep(sleep_timer)
        pids = update_running_pids(pids)

def compute_yesterday_ranking():
    """
        if the bview file has been generated at midnight, it is better
        to compute the ranking of "yesterday"
    """
    raw_data = os.path.join(root_dir,config.get('directories','raw_data'))
    ts_file = os.path.join(raw_data, path_bviewtimesamp)
    if os.path.exists(ts_file):
        ts = open(ts_file, 'r').read()
        redis.Redis(port = int(config.get('redis','port_master')),
                db = config.get('redis','history')).set('latest_ranking', ts)
        ts = ts.split()
        if int(ts[1]) == 0:
            return True
    return False

def prepare_bview_file():
    publisher.info('Start converting binary bview file in plain text...')

    # create the plain text dump from the binary dump
    output = open(os.path.join(bview_dir, 'bview'), 'wr')
    nul_f = open(os.devnull, 'w')
    p_bgp = Popen([bgpdump , filename], stdout=PIPE, stderr = nul_f)
    for line in p_bgp.stdout:
        output.write(line)
    nul_f.close()
    output.close()
    publisher.info('Convertion finished, start splitting...')

    # Split the plain text file
    fs = FilesSplitter(output.name, number_of_splits)
    splitted_files = fs.fplit()
    publisher.info('Splitting finished.')

    # Flush the old routing database and launch the population of
    # the new database
    routing_db.flushdb()

    publisher.info('Start pushing all routes...')
    run_splitted_processing(split_procs, pushing_process_service,
            splitted_files)
    publisher.info('All routes pushed.')

    # Remove the binary and the plain text files
    os.unlink(output.name)
    os.unlink(filename)

def reset_db_daily():
    # Clean the whole database and regenerate it (like this we do not
    # keep data of the old rankings)
    report = ReportsGenerator()
    report.flush_temp_db()
    report.build_reports_lasts_days(days_history_cache)

    # date used to generate a ranking with the data in the database at
    # this point
    date = (datetime.date.today() - datetime.timedelta(1)).isoformat()
    return date

def prepare_keys_for_ranking():
    # Add all announced subnets by ASN
    pipeline = history_db_static.pipeline()
    for asn in routing_db.smembers('asns'):
        blocks = routing_db.smembers(asn)
        pipeline.sadd('{asn}|{date}|clean_set'.format(asn = asn,
            date = date), *blocks)
        temp_db.sadd('full_asn_db', *[str(IPy.IP(b)[0]) for b in blocks])
        temp_db.sadd('no_asn', 'full_asn_db')
    pipeline.execute()

    # Cleanup the old keys, setup the list of asns to rank
    sources = global_db.smembers('{date}|sources'.format(date = date))

    pipeline = history_db.pipeline()
    pipeline_static = history_db_static.pipeline()
    to_delete = []
    for source in sources:
        asns = global_db.smembers('{date}|{source}|asns_details'.format(
            date = date, source = source))
        for asn in asns:
            global_asn = asn.split('|')[0]
            asn_key_v4 = '{asn}|{date}|{source}|rankv4'.format(
                    asn = global_asn, date = date, source = source)
            asn_key_v6 = '{asn}|{date}|{source}|rankv6'.format(
                    asn = global_asn, date = date, source = source)
            to_delete.append(asn_key_v4)
            to_delete.append(asn_key_v6)

            pipeline.sadd(key_to_rank, '{asn}|{date}|{source}'.format(
                asn = asn, date = date, source = source))
    to_delete = set(to_delete)
    if len(to_delete) > 0:
        pipeline_static.delete(*to_delete)
    else:
        publisher.error('You *do not* have anything to rank!')
    pipeline.execute()
    pipeline_static.execute()


if __name__ == '__main__':

    publisher.channel = 'Ranking'

    config = ConfigParser.RawConfigParser()
    config_file = "/etc/bgpranking/bgpranking.conf"
    config.read(config_file)
    root_dir = config.get('directories','root')
    sys.path.append(os.path.join(root_dir,
        config.get('directories','libraries')))
    from helpers.initscript import *
    from helpers.files_splitter import FilesSplitter
    from ranking.reports_generator import ReportsGenerator
    services_dir = os.path.join(root_dir,
            config.get('directories','services'))
    bgpdump = os.path.join(root_dir, path_to_bgpdump_bin)

    routing_db = redis.Redis(port=int(config.get('redis','port_cache')),
            db = config.get('redis','routing'))
    global_db = redis.Redis(port=int(config.get('redis','port_master')),
            db = config.get('redis','global'))
    history_db = redis.Redis(port=int(config.get('redis','port_cache')),
            db = config.get('redis','history'))
    history_db_static = redis.Redis(port = int(config.get('redis','port_master')),
            db = config.get('redis','history'))
    temp_db = redis.Redis(port = int(config.get('redis','port_cache')),
            db=int(config.get('redis','temp')))

    filename = os.path.join(root_dir, config.get('directories','raw_data'),
            path_bviewfile)
    bview_dir = os.path.dirname(filename)

    pushing_process_service = os.path.join(services_dir, "pushing_process")
    ranking_process_service = os.path.join(services_dir, "ranking_process")

    # Wait a bit until the bview file is downloaded
    time.sleep(60)

    while 1:
        if not os.path.exists(filename) or history_db.exists(key_to_rank):
            # wait for a new file
            time.sleep(bview_check_interval)
            continue

        prepare_bview_file()

        if compute_yesterday_ranking():
            date = reset_db_daily()
        else:
            date = datetime.date.today().isoformat()

        prepare_keys_for_ranking()

        service_start_multiple(ranking_process_service, rank_procs)

        while history_db.scard(key_to_rank) > 0:
            # wait for a new file
            time.sleep(sleep_timer)
        rmpid(ranking_process_service)
        # Save the number of asns known by the RIPE
        history_db_static.set('{date}|amount_asns'.format(date = date),
                routing_db.dbsize())
        routing_db.flushdb()
        publisher.info('Updating the reports...')
        ReportsGenerator().build_reports(date)
        publisher.info('...done.')
