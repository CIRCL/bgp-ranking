#!/usr/bin/python
# -*- coding: utf-8 -*-


import fileinput
import api
import constraints as c
import csv


c.last_days = 365

aggregated = {}
asns = []
for line in fileinput.input():
    if line[0] == '#':
        continue
    line = line.split('|')
    if line[2] != 'asn':
        continue
    asn = line[3]
    if asn in asns:
        continue
    asns.append(asn)
    informations = api.get_asn_informations(asn)
    if informations.get('data') is None:
        continue
    for date, value in informations['data'].iteritems():
        if aggregated.get(date) is None:
            aggregated[date] = 1
        aggregated[date] += value['total']

sort = sorted([(date, value) for date, value in aggregated.iteritems()])

with open('lu_year.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile)
    for date, value in reversed(sort):
        writer.writerow([date, value])

with open('lu_6_month.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile)
    i = 0
    for date, value in reversed(sort):
        writer.writerow([date, value])
        i += 1
        if i >= 180:
            break

with open('lu_3_month.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile)
    i = 0
    for date, value in reversed(sort):
        writer.writerow([date, value])
        i += 1
        if i >= 90:
            break

with open('lu_1_month.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile)
    i = 0
    for date, value in reversed(sort):
        writer.writerow([date, value])
        i += 1
        if i >= 30:
            break

with open('lu_2_weeks.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile)
    i = 0
    for date, value in reversed(sort):
        writer.writerow([date, value])
        i += 1
        if i >= 15:
            break

with open('lu_1_week.csv', 'wb') as csvfile:
    writer = csv.writer(csvfile)
    i = 0
    for date, value in reversed(sort):
        writer.writerow([date, value])
        i += 1
        if i >= 7:
            break

