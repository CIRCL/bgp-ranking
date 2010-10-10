#!/bin/bash -v

source common.source.sh

${REDIS_ROOT}/redis-cli flushall

./init_databases.sh

cd $OLD_PWD