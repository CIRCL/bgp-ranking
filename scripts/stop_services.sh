#!/bin/bash -v

source common.source.sh

OLD_PWD=$PWD
cd ${BGP_RANKING_ROOT}/etc/init.d/

$PYTHON start_fetch_raw_files.py stop
$PYTHON start_parse_raw_files.py stop
$PYTHON start_get_ris_entries.py stop
$PYTHON start_fetch_whois_entries.py stop

cd $OLD_PWD

ps aux |grep python
