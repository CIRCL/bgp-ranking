set -e

PREFIX="${HOME}/gits/"
BGP_RANKING_ROOT="${PREFIX}bgp-ranking"
#PYTHON="${PREFIX}/Python-2.7/python"
PYTHON="/usr/bin/python"
#NICE="nice -n15 ionice -n2 -c7"
NICE=""


REDIS_SERVER="/usr/bin/redis-server"
REDIS_CLIENT="/usr/bin/redis-cli"
REDIS_CONFIG="${BGP_RANKING_ROOT}/etc/"
