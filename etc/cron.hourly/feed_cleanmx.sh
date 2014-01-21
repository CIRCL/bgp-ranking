#!/bin/sh
# Version 1.01 15th Jan 2014
# Author: Gerhard W. Recher (gerhard.recher@net4sec.com)
# BGP Ranking related Changes: Raphaël Vinot
#
STRICT=yes # Set this to 'yes' to limit execution of feed only in one instance in case cron will schedule this to often.

ROOT_BGPRANKING="/home/raphael/gits/bgp-ranking/var/raw_data/cleanmx/"
USER_BGPRANKING="raphael"
GROUP_BGPRANKING="raphael"

set -x
set -e

if [ "$STRICT" = "yes" ]; then
  pushd ${ROOT_BGPRANKING}
  if [ ! -f ./feeds.lock ]; then
    DAY=`date --date='today' +%d`;
    MONTH=`date  --date='today' +%m`;
    YEAR=`date  --date='today' +%Y`;
    HOUR=`date  --date='today' +%H`;
    touch ./feeds.lock
    #
    # adjust working directory
    uid=${USER_BGPRANKING}
    gid=${GROUP_BGPRANKING}
    format=xml
    #
    # fetch watermarks of last run
    aviruses=`cat ./aviruses.last`
    aphishing=`cat ./aphishing.last`
    aportals=`cat ./aportals.last`
    #azombies=`cat ./azombies.last`
    #
    # Get delta since last run
    wget "http://support.clean-mx.de/clean-mx/xmlviruses?format=$format&delta=$aviruses" \
            -O ./malwares/temp/hourly.viruses.$YEAR.$MONTH.$DAY.$HOUR.$format
    wget "http://support.clean-mx.de/clean-mx/xmlportals?format=$format&delta=$aportals" \
            -O ./portals/temp/hourly.portals.$YEAR.$MONTH.$DAY.$HOUR.$format
    wget "http://support.clean-mx.de/clean-mx/xmlphishing?format=$format&delta=$aphishing" \
            -O ./phishing/temp/hourly.phishing.$YEAR.$MONTH.$DAY.$HOUR.$format
    #wget "http://support.clean-mx.de/clean-mx/xmlpublog?format=$format&delta=$azombies" \
    #        -O ./zombies/temp/hourly.zombies.$YEAR.$MONTH.$DAY.$HOUR.$format
    #
    # get the watermarks out of result
    if [ "$format" = "xml" ]; then
        aviruses=`head -10 ./malwares/temp/hourly.viruses.$YEAR.$MONTH.$DAY.$HOUR.$format|grep id|cut -f2 -d ">"|cut -f1 -d "<"`
        aphishing=`head -10 ./phishing/temp/hourly.phishing.$YEAR.$MONTH.$DAY.$HOUR.$format|grep id|cut -f2 -d ">"|cut -f1 -d "<"`
        aportals=`head -10 ./portals/temp/hourly.portals.$YEAR.$MONTH.$DAY.$HOUR.$format|grep id|cut -f2 -d ">"|cut -f1 -d "<"`
    else

        aviruses=`head -2 ./malwares/temp/hourly.viruses.$YEAR.$MONTH.$DAY.$HOUR.$format|cut -f4 -d "\""|grep -v id`
        aphishing=`head -2 ./phishing/temp/hourly.phishing.$YEAR.$MONTH.$DAY.$HOUR.$format|cut -f4 -d "\""|grep -v id`
        aportals=`head -2 ./portals/temp/hourly.portals.$YEAR.$MONTH.$DAY.$HOUR.$format|cut -f4 -d "\""|grep -v id`
    fi
    if [ "$aviruses" = "" ]; then
        # no progress
        echo "stall viruses"
        rm -f ./malwares/temp/hourly.viruses.$YEAR.$MONTH.$DAY.$HOUR.$format
    else
        # new
        echo $aviruses > ./aviruses.last
        mv ./malwares/temp/hourly.viruses.$YEAR.$MONTH.$DAY.$HOUR.$format ./malwares/
    fi
    if [ "$aphishing" = "" ]; then
        # no progress
        echo "stall phishing"
        rm -f ./phishing/temp/hourly.phishing.$YEAR.$MONTH.$DAY.$HOUR.$format
    else
        # new
        echo $aphishing > ./aphishing.last
        mv ./phishing/temp/hourly.phishing.$YEAR.$MONTH.$DAY.$HOUR.$format ./phishing/
    fi
    if [ "$aportals" = "" ]; then
        # no progress
        echo "stall portals"
        rm ./portals/temp/hourly.portals.$YEAR.$MONTH.$DAY.$HOUR.$format
    else
        # new
        echo $aportals > ./aportals.last
        mv ./portals/temp/hourly.portals.$YEAR.$MONTH.$DAY.$HOUR.$format ./portals/
    fi
    # adjust ownership
    chown -R $uid:$gid ./*
    rm ./feeds.lock
  fi
  popd
fi
