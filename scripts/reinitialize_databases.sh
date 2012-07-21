#!/bin/bash -v

source common.source.sh

${REDIS_ROOT}/redis-cli -n 4 flushdb

./init_databases.sh

cd $OLD_PWD