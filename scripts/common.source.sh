set -e

PREFIX="${HOME}/gits/"
BGP_RANKING_ROOT="${PREFIX}bgp-ranking"
#PYTHON="${PREFIX}/Python-2.7/python"
PYTHON="/usr/bin/python"
#NICE="nice -n15 ionice -n2 -c7"
NICE=""

REDIS_ROOT="/home/raphael/gits/redis/src/"

REDIS_SERVER="./redis-server"
REDIS_CLIENT="./redis-cli"
REDIS_CONFIG="${BGP_RANKING_ROOT}/etc/"
