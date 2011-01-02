#!/bin/bash -v

source common.source.sh

OLD_PWD=$PWD
cd ${REDIS_ROOT}

./redis-cli -p 6382 shutdown

./redis-cli -p 6380 shutdown
./redis-cli -p 6381 shutdown
./redis-cli -p 6379 shutdown

cd $OLD_PWD
