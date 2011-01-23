#!/bin/bash -v

source common.source.sh

OLD_PWD=$PWD
cd ${REDIS_ROOT}

./redis-server ${REDIS_CONFIG}/redis.conf
./redis-server ${REDIS_CONFIG}/redis-slave.conf
# ./redis-server ${REDIS_CONFIG}/redis-slave2.conf

./redis-server ${REDIS_CONFIG}/redis-cache.conf


cd $OLD_PWD
