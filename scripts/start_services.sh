#!/bin/bash -v

source common.source.sh

OLD_PWD=$PWD
cd ${BGP_RANKING_ROOT}/etc/init.d/

#NICE="nice -n15 ionice -n7 -c2"

$NICE $PYTHON start_fetch_raw_files.py start
$NICE $PYTHON start_parse_raw_files.py start
$NICE $PYTHON start_get_ris_entries.py start
$NICE $PYTHON start_fetch_whois_entries.py start

cd $OLD_PWD
