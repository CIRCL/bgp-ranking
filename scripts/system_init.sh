#!/bin/bash

mkdir -p /etc/bgpranking/
pushd /etc/bgpranking
ln -s ~/gits/bgp-ranking/etc/bgp-ranking.conf bgpranking.conf
ln -s ~/gits/bgp-ranking/etc/bgp-ranking.conf.redis bgpranking.conf.redis
popd
