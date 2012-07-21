#!/bin/bash -v

source common.source.sh

${REDIS_CLIENT} -p 6382 save
${REDIS_CLIENT} -p 6382 shutdown

${REDIS_CLIENT} -p 6379 save
${REDIS_CLIENT} -p 6379 shutdown

