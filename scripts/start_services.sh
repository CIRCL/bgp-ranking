#!/bin/bash -v

source common.source.sh

OLD_PWD=$PWD
cd ${BGP_RANKING_ROOT}/etc/init.d/

$NICE $PYTHON start_db_input.py start
$NICE $PYTHON start_module_manager.py start
$NICE $PYTHON start_ris.py start
$NICE $PYTHON start_fetch_ris_entries.py start
#$NICE $PYTHON start_microblog.py start

# Desactivated by default
#$NICE $PYTHON start_sort_whois_queries.py start
#$NICE $PYTHON start_get_whois_entries.py start

cd $OLD_PWD
