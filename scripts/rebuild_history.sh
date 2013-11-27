#!/bin/bash

set -e
set -x

DIR=temp

mkdir ${DIR}/bgp/tmp


while read date ; do
    echo $date

    ../bin/services/fetch_bview.py -d $date -p ${DIR} &
    ../bin/services/push_update_routing.py -d $date -p ${DIR}
done < dates.txt
