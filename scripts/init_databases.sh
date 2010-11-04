#!/bin/bash -v

source common.source.sh

OLD_PWD=$PWD
cd ${BGP_RANKING_ROOT}/lib/db_init/

$PYTHON init_assignations_redis.py
$PYTHON init_ranking.py

cd $OLD_PWD
