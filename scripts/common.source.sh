set -e

PREFIX="${HOME}/gits/"
BGP_RANKING_ROOT="${PREFIX}bgp-ranking"
PYTHON="/usr/bin/python"
NICE=""

REDIS_ROOT="${PREFIX}redis/src/"

REDIS_SERVER="./redis-server"
REDIS_CLIENT="./redis-cli"
REDIS_CONFIG="${BGP_RANKING_ROOT}/etc/"
