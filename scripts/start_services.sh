#!/bin/bash -v

source common.source.sh

OLD_PWD=$PWD
cd ${BGP_RANKING_ROOT}/etc/init.d/

$NICE $PYTHON start_db_input.py start
$NICE $PYTHON start_fetch_raw_files.py start
$NICE $PYTHON start_parse_raw_files.py start
$NICE $PYTHON start_ris.py start
$NICE $PYTHON start_fetch_whois_entries.py start

# Desactivated by default
#$NICE $PYTHON start_sort_whois_queries.py start
#$NICE $PYTHON start_get_whois_entries.py start

cd $OLD_PWD
