#!/bin/bash -v

source common.source.sh

pushd ${REDIS_ROOT}

echo -n "Starting main redis instance..."
${REDIS_SERVER} ${REDIS_CONFIG}/redis.conf
echo " done."

echo -n "Starting cache redis instance..."
${REDIS_SERVER} ${REDIS_CONFIG}/redis-cache.conf
echo " done."
popd
