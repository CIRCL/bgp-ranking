#!/bin/bash

START_DATE="2011-06-01"
END_DATE="2013-08-01"


echo $START_DATE > dates.txt

DATE=$START_DATE
while [ "$DATE" != "$END_DATE" ] ; do
    DATE=$( date +%Y-%m-%d -d "$DATE -d 1day" )
    echo $DATE >> dates.txt
done
