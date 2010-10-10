#!/bin/bash -v

source common.source.sh

OLD_PWD=$PWD
cd ${BGP_RANKING_ROOT}/etc/init.d/

$NICE $PYTHON start_fetch_bview.py stop
$NICE $PYTHON start_push_update_routing.py stop

cd $OLD_PWD

ps aux |grep python