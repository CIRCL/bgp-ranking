#!/bin/bash -v

source common.source.sh

OLD_PWD=$PWD
cd ${BGP_RANKING_ROOT}/etc/init.d/

#NICE="nice -n15 ionice -n7 -c2"

$NICE $PYTHON start_fetch_bview.py start
$NICE $PYTHON start_push_update_routing.py start

cd $OLD_PWD
